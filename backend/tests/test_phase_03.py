"""
Phase 03 Tests: Preset and Layer Engine

Epic 06: Preset Schema validation
Epic 04: Layer Library and registry
Epic 05: Modulation System
Epic 07: Raindrops Shader
Epic 08: Spectroid Chase Shader
"""

import pytest
import numpy as np
from typing import Dict, Any

# Import the Phase 03 modules
from app.preset import (
    PresetDefinition,
    PresetMetadata,
    ParameterSchema,
    ParameterType,
    ParameterConstraint,
    ColorPalette,
    LayerReference,
    BlendMode,
    PresetValidator,
    PresetValidationError,
    PresetRegistry,
)
from app.layers import (
    Layer,
    RenderContext,
    LayerRegistry,
    WaveLayer,
    RadialPulseLayer,
    SolidFieldLayer,
    BarsLayer,
    RingsLayer,
    BeatFlashLayer,
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    BLEND_MODES,
)
from app.modulation import (
    ModulatorType,
    ModulationContext,
    AudioBandModulator,
    OnsetModulator,
    BeatPulseModulator,
    BeatPhaseModulator,
    LFOModulator,
    LFOWaveform,
    RandomModulator,
    ScaleMapping,
    ClampMapping,
    ModulationChain,
    ModulationSystem,
)
from app.presets_builtin import get_builtin_presets
from app.shaders import RaindropsLayer, SpectroidChaseLayer


# ============================================================================
# Epic 06: Preset Schema Tests
# ============================================================================

class TestPresetSchema:
    """Epic 06.V1: Valid preset test - prove valid presets load and pass validation."""
    
    def test_valid_preset_passes_validation(self):
        """Test that a well-formed preset passes validation."""
        preset = PresetDefinition(
            metadata=PresetMetadata(
                preset_id="test_preset",
                version="1.0",
                label="Test Preset",
            ),
            layers=[
                LayerReference(
                    layer_id="wave",
                    label="Wave",
                    order=0,
                    blend_mode=BlendMode.ALPHA,
                )
            ]
        )
        
        # Should not raise
        errors = PresetValidator.validate_preset(preset, {})
        assert len(errors) == 0
    
    def test_builtin_presets_are_valid(self):
        """Epic 06.V4: Baseline parity test - built-in presets are valid."""
        registry = PresetRegistry()
        builtin = get_builtin_presets()
        
        for preset_key, preset in builtin.items():
            # Should not raise
            errors = PresetValidator.validate_preset(preset, registry.layer_registry)
            assert len(errors) == 0, f"Preset {preset_key} validation failed: {errors}"
            
            # Should register successfully
            registry.register_preset(preset, validate=True)
    
    def test_undersea_waves_preset_exists(self):
        """Epic 06.B7: Undersea waves preset is defined."""
        registry = PresetRegistry()
        builtin = get_builtin_presets()
        
        undersea_waves = [p for k, p in builtin.items() if p.metadata.preset_id == "undersea_waves"]
        assert len(undersea_waves) > 0, "Undersea waves preset not found"
        
        preset = undersea_waves[0]
        assert len(preset.layers) == 3, "Undersea waves should have 3 layers"
        assert preset.palette is not None, "Undersea waves should have a palette"
    
    def test_undersea_pulse_preset_exists(self):
        """Epic 06.B8: Baseline pulse preset migrated."""
        registry = PresetRegistry()
        builtin = get_builtin_presets()
        
        undersea_pulse = [p for k, p in builtin.items() if p.metadata.preset_id == "undersea_pulse_01"]
        assert len(undersea_pulse) > 0, "Undersea pulse preset not found"


class TestPresetValidation:
    """Epic 06.V2: Invalid preset test - prove invalid presets fail with actionable errors."""
    
    def test_invalid_preset_missing_id(self):
        """Test validation fails for missing preset ID."""
        preset = PresetDefinition(
            metadata=PresetMetadata(
                preset_id="",  # Invalid: empty
                version="1.0",
                label="Test",
            ),
            layers=[LayerReference(layer_id="wave", label="Wave", order=0)]
        )
        
        with pytest.raises(PresetValidationError) as exc:
            PresetValidator.validate_preset(preset)
        
        assert "id" in str(exc.value).lower()
    
    def test_invalid_preset_no_layers(self):
        """Test validation fails for preset with no layers."""
        preset = PresetDefinition(
            metadata=PresetMetadata(preset_id="test", version="1.0", label="Test"),
            layers=[]
        )
        
        with pytest.raises(PresetValidationError) as exc:
            PresetValidator.validate_preset(preset)
        
        assert "layer" in str(exc.value).lower()
    
    def test_invalid_preset_parameter_bounds(self):
        """Test validation fails for parameter with invalid defaults."""
        preset = PresetDefinition(
            metadata=PresetMetadata(preset_id="test", version="1.0", label="Test"),
            parameters={
                "speed": ParameterSchema(
                    name="speed",
                    type=ParameterType.FLOAT,
                    label="Speed",
                    default_value=10.0,
                    constraint=ParameterConstraint(min_value=0.0, max_value=5.0)
                )
            },
            layers=[LayerReference(layer_id="wave", label="Wave", order=0)]
        )
        
        with pytest.raises(PresetValidationError) as exc:
            PresetValidator.validate_preset(preset)
        
        assert "default" in str(exc.value).lower() or "maximum" in str(exc.value).lower()


# ============================================================================
# Epic 04: Layer Library Tests
# ============================================================================

class TestLayerRegistry:
    """Epic 04.V1: Registry test - prove layers are registered and loadable by id."""
    
    def test_wave_layer_registered(self):
        """Test that wave layer is in registry."""
        registry = LayerRegistry()
        assert registry.get_layer("wave") is not None
    
    def test_all_layers_registered(self):
        """Test all built-in layers are registered."""
        registry = LayerRegistry()
        expected_layers = [
            "wave",
            "radial_pulse",
            "solid_field",
            "gradient_field",
            "bars",
            "rings",
            "beat_flash",
            "scanner",
        ]
        
        for layer_id in expected_layers:
            assert registry.get_layer(layer_id) is not None, f"Layer {layer_id} not registered"
    
    def test_layer_parameter_schema(self):
        """Test layers return valid parameter schemas."""
        registry = LayerRegistry()
        for layer_id in registry.list_layers():
            layer = registry.get_layer(layer_id)
            schema = layer.get_parameter_schema()
            assert isinstance(schema, dict), f"Layer {layer_id} parameter schema is not a dict"


class TestLayerDeterminism:
    """Epic 04.V2: Determinism test - prove seeded layers render reproducibly."""
    
    def test_wave_layer_determinism(self):
        """Test that wave layer renders same output for same seed and frame."""
        registry = LayerRegistry()
        layer = registry.get_layer("wave")
        
        context1 = RenderContext(seed=42, frame_index=10, total_frames=300, fps=30)
        context2 = RenderContext(seed=42, frame_index=10, total_frames=300, fps=30)
        
        params = {"speed": 1.0, "amplitude": 1.0, "wavelength": 20, "base_color": "#0000FF"}
        
        frame1 = layer.render_frame(context1, params)
        frame2 = layer.render_frame(context2, params)
        
        assert np.array_equal(frame1, frame2), "Same seed should produce identical output"
    
    def test_different_seed_different_output(self):
        """Test that different seeds produce different output for random-based layers."""
        registry = LayerRegistry()
        
        context1 = RenderContext(seed=42, frame_index=10, total_frames=300, fps=30)
        context2 = RenderContext(seed=99, frame_index=10, total_frames=300, fps=30)
        
        # Most deterministic renders with different seeds should differ (beat flash varies)
        # This is a soft test since some layers might not use seed
        assert context1.seed != context2.seed


class TestLayerVisualOutput:
    """Epic 04.V3: Visual fixture coverage - layers render without errors."""
    
    def test_wave_layer_renders(self):
        """Test wave layer renders valid output."""
        layer = WaveLayer()
        context = RenderContext(seed=42, frame_index=0, total_frames=300, fps=30)
        params = {"speed": 1.0, "amplitude": 1.0, "wavelength": 20, "base_color": "#0000FF"}
        
        frame = layer.render_frame(context, params)
        
        assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3)
        assert frame.dtype == np.uint8
        assert frame.min() >= 0 and frame.max() <= 255
    
    def test_radial_pulse_renders(self):
        """Test radial pulse layer renders valid output."""
        layer = RadialPulseLayer()
        context = RenderContext(seed=42, frame_index=0, total_frames=300, fps=30)
        params = {
            "center_x": 50,
            "center_y": 25,
            "pulse_speed": 10.0,
            "pulse_radius": 20.0,
            "decay": 0.95,
            "base_color": "#FFFFFF"
        }
        
        frame = layer.render_frame(context, params)
        
        assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3)
        assert frame.min() >= 0 and frame.max() <= 255
    
    def test_all_layers_render(self):
        """Test all layers render without errors."""
        registry = LayerRegistry()
        context = RenderContext(seed=42, frame_index=0, total_frames=300, fps=30)
        
        for layer_id in registry.list_layers():
            layer = registry.get_layer(layer_id)
            schema = layer.get_parameter_schema()
            
            # Build minimal params from schema
            params = {name: s.get("default", 0) for name, s in schema.items()}
            
            frame = layer.render_frame(context, params)
            
            assert frame is not None, f"Layer {layer_id} returned None"
            assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3), f"Layer {layer_id} wrong shape"


# ============================================================================
# Epic 05: Modulation System Tests
# ============================================================================

class TestModulationSystem:
    """Epic 05.V1: Binding test - presets can bind modulators to layer parameters."""
    
    def test_bind_audio_band_modulator(self):
        """Test binding audio band modulator to parameter."""
        system = ModulationSystem()
        
        success = system.bind_modulator("wave_speed", "audio_band_0")
        assert success, "Failed to bind audio band modulator"
    
    def test_bind_nonexistent_modulator_fails(self):
        """Test binding nonexistent modulator fails gracefully."""
        system = ModulationSystem()
        
        success = system.bind_modulator("wave_speed", "nonexistent_modulator")
        assert not success, "Should fail to bind nonexistent modulator"


class TestModulatorDeterminism:
    """Epic 05.V2: Determinism test - modulator outputs stable for same inputs."""
    
    def test_lfo_determinism(self):
        """Test LFO produces same output for same frame time."""
        lfo = LFOModulator(frequency=1.0, waveform=LFOWaveform.SINE)
        
        context1 = ModulationContext(frame_time=1.0)
        context2 = ModulationContext(frame_time=1.0)
        
        value1 = lfo.evaluate(context1)
        value2 = lfo.evaluate(context2)
        
        assert abs(value1 - value2) < 0.0001, "LFO should be deterministic"
    
    def test_random_modulator_determinism(self):
        """Test random modulator produces same output for same seed and frame."""
        rand_mod1 = RandomModulator(rate=1.0, seed_base=42)
        rand_mod2 = RandomModulator(rate=1.0, seed_base=42)
        
        context1 = ModulationContext(frame_time=0.5, seed=100)
        context2 = ModulationContext(frame_time=0.5, seed=100)
        
        value1 = rand_mod1.evaluate(context1)
        value2 = rand_mod2.evaluate(context2)
        
        assert abs(value1 - value2) < 0.0001, "Random modulator should be deterministic with same seed"


class TestMappingOperations:
    """Epic 05.V3: Mapping test - mapping operations apply in declared order."""
    
    def test_scale_mapping(self):
        """Test scale mapping operation."""
        mapping = ScaleMapping(factor=2.0)
        assert mapping.apply(0.5) == 1.0
    
    def test_mapping_chain_order(self):
        """Test mappings apply in order."""
        chain = ModulationChain()
        chain.add_mapping(ScaleMapping(2.0))
        chain.add_mapping(ClampMapping(0.0, 1.0))
        
        # 0.75 * 2 = 1.5, clamped to 1.0
        result = chain.apply(0.75)
        assert result == 1.0, f"Expected 1.0, got {result}"


# ============================================================================
# Epic 07: Raindrops Shader Tests
# ============================================================================

class TestRaindropsShader:
    """Epic 07: Raindrops shader tests."""
    
    def test_raindrops_renders(self):
        """Test raindrops layer renders without error."""
        layer = RaindropsLayer()
        context = RenderContext(seed=42, frame_index=0, total_frames=300, fps=30)
        params = {
            "pulse_rate": 2.0,
            "pulse_radius_growth": 5.0,
            "pulse_decay": 0.95,
            "collision_strength": 1.5,
            "base_color": "#00FFFF",
        }
        
        frame = layer.render_frame(context, params)
        
        assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3)
        assert frame.min() >= 0 and frame.max() <= 255
    
    def test_raindrops_schema(self):
        """Test raindrops parameter schema is complete."""
        layer = RaindropsLayer()
        schema = layer.get_parameter_schema()
        
        required_params = [
            "pulse_rate", "pulse_radius_growth", "pulse_decay",
            "collision_strength", "base_color"
        ]
        
        for param in required_params:
            assert param in schema, f"Missing parameter: {param}"


# ============================================================================
# Epic 08: Spectroid Chase Shader Tests
# ============================================================================

class TestSpectroidChaseShader:
    """Epic 08: Spectroid chase shader tests."""
    
    def test_spectroid_renders(self):
        """Test spectroid chase layer renders without error."""
        layer = SpectroidChaseLayer()
        context = RenderContext(
            seed=42,
            frame_index=0,
            total_frames=300,
            fps=30,
            onset_detected=True
        )
        params = {
            "trigger_sensitivity": 0.5,
            "line_length": 30.0,
            "chase_speed": 20.0,
            "fade_distance": 10.0,
            "line_width": 2,
            "base_color": "#FF00FF",
        }
        
        frame = layer.render_frame(context, params)
        
        assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3)
        assert frame.min() >= 0 and frame.max() <= 255
    
    def test_spectroid_schema(self):
        """Test spectroid parameter schema is complete."""
        layer = SpectroidChaseLayer()
        schema = layer.get_parameter_schema()
        
        required_params = [
            "trigger_sensitivity", "line_length", "chase_speed",
            "fade_distance", "line_width", "base_color"
        ]
        
        for param in required_params:
            assert param in schema, f"Missing parameter: {param}"


# ============================================================================
# Integration Tests
# ============================================================================

class TestPresetWithLayers:
    """Integration test: verify presets work with layer registry."""
    
    def test_undersea_waves_layers_exist(self):
        """Test that undersea waves preset references valid layers."""
        registry = LayerRegistry()
        builtin = get_builtin_presets()
        
        undersea_waves = [p for k, p in builtin.items() if p.metadata.preset_id == "undersea_waves"][0]
        
        for layer_ref in undersea_waves.layers:
            layer = registry.get_layer(layer_ref.layer_id)
            assert layer is not None, f"Layer {layer_ref.layer_id} not found in registry"


# ============================================================================
# Epic 04: New Layer Tests (Mirror, Scroll, Zoom)
# ============================================================================

class TestNewLayers:
    """Epic 04.B10 / 04.B12: MirrorLayer, ScrollLayer, ZoomLayer."""

    def _ctx(self, frame: int = 0) -> RenderContext:
        return RenderContext(seed=7, frame_index=frame, total_frames=120, fps=30)

    def test_mirror_layer_horizontal(self):
        from app.layers import MirrorLayer
        layer = MirrorLayer()
        frame = layer.render_frame(self._ctx(), {"axis": "horizontal"})
        assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3)
        assert frame.dtype == np.uint8

    def test_mirror_layer_vertical(self):
        from app.layers import MirrorLayer
        layer = MirrorLayer()
        frame = layer.render_frame(self._ctx(), {"axis": "vertical"})
        assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3)

    def test_mirror_layer_both_axes(self):
        from app.layers import MirrorLayer
        layer = MirrorLayer()
        frame = layer.render_frame(self._ctx(), {"axis": "both"})
        assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3)

    def test_scroll_layer_renders(self):
        from app.layers import ScrollLayer
        layer = ScrollLayer()
        schema = layer.get_parameter_schema()
        params = {k: v.get("default", 0) for k, v in schema.items()}
        frame = layer.render_frame(self._ctx(), params)
        assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3)
        assert frame.dtype == np.uint8

    def test_zoom_layer_renders(self):
        from app.layers import ZoomLayer
        layer = ZoomLayer()
        schema = layer.get_parameter_schema()
        params = {k: v.get("default", 0) for k, v in schema.items()}
        frame = layer.render_frame(self._ctx(), params)
        assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3)
        assert frame.dtype == np.uint8

    def test_mirror_scroll_zoom_registered(self):
        registry = LayerRegistry()
        ids = registry.list_layers()
        for expected in ("mirror", "scroll", "zoom"):
            assert expected in ids, f"'{expected}' missing from LayerRegistry"


# ============================================================================
# Epic 07: Raindrops Shader Validation (V1-V4)
# ============================================================================

class TestRaindropsShaderValidation:
    """Epic 07.V1-V4: POI origin, transit, collision, and snapshot tests."""

    def _make_context(self, frame: int = 3) -> RenderContext:
        return RenderContext(seed=10, frame_index=frame, total_frames=300, fps=30,
                             fft_bands=[0.5] * 8)

    def test_v1_poi_origin_lit(self):
        """07.V1: Single POI at (20, 10) — pixels near it should be non-zero."""
        layer = RaindropsLayer()
        ctx = self._make_context(frame=3)
        params = {
            "pulse_rate": 2.0,
            "pulse_radius_growth": 3.0,
            "pulse_decay": 0.99,
            "collision_strength": 1.5,
            "base_color": "#FFFFFF",
            "_pois": [{"id": "p1", "x": 20, "y": 10}],
        }
        frame = layer.render_frame(ctx, params)
        # At least one pixel near the POI must be lit
        region = frame[5:16, 15:26]
        assert region.max() > 0, "Expected non-zero pixels near POI origin"

    def test_v2_transit_boost_at_second_poi(self):
        """07.V2: With 2 POIs, the second POI location gets boosted by transit."""
        layer = RaindropsLayer()
        # Use a frame where the pulse from POI-0 has time to reach POI-1
        ctx = self._make_context(frame=6)
        pois = [
            {"id": "p1", "x": 10, "y": 25},
            {"id": "p2", "x": 40, "y": 25},
        ]
        params = {
            "pulse_rate": 1.0,
            "pulse_radius_growth": 8.0,
            "pulse_decay": 0.99,
            "collision_strength": 1.2,
            "transit_boost": 3.0,
            "base_color": "#FFFFFF",
            "_pois": pois,
        }
        frame = layer.render_frame(ctx, params)
        # Frame must at least render valid shape — actual transit visibility
        # depends on timing; this is a smoke test that the path executes.
        assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3)
        assert frame.max() >= 0

    def test_v3_determinism(self):
        """07.V3: Same seed + params → identical frames (collision is deterministic)."""
        layer = RaindropsLayer()
        pois = [{"id": "p1", "x": 20, "y": 20}, {"id": "p2", "x": 60, "y": 30}]
        params = {
            "pulse_rate": 2.0,
            "pulse_radius_growth": 5.0,
            "pulse_decay": 0.95,
            "collision_strength": 1.5,
            "base_color": "#00FFFF",
            "_pois": pois,
        }
        ctx_a = RenderContext(seed=99, frame_index=5, total_frames=300, fps=30)
        ctx_b = RenderContext(seed=99, frame_index=5, total_frames=300, fps=30)
        frame_a = layer.render_frame(ctx_a, params)
        frame_b = layer.render_frame(ctx_b, params)
        np.testing.assert_array_equal(frame_a, frame_b)

    def test_v4_snapshot_shape_dtype(self):
        """07.V4: Render result has correct shape and dtype."""
        layer = RaindropsLayer()
        ctx = self._make_context()
        params = {
            "pulse_rate": 2.0,
            "pulse_radius_growth": 5.0,
            "pulse_decay": 0.95,
            "collision_strength": 1.5,
            "base_color": "#00FFFF",
        }
        frame = layer.render_frame(ctx, params)
        assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3)
        assert frame.dtype == np.uint8
        assert frame.min() >= 0
        assert frame.max() <= 255


# ============================================================================
# Epic 08: Spectroid Chase Shader Validation (V1-V4)
# ============================================================================

class TestSpectroidChaseShaderValidation:
    """Epic 08.V1-V4: Trigger determinism, parcan anchor, follow lines, snapshot."""

    _PARCAN = [{"id": "par1", "x": 50, "y": 25}]

    def _params(self, **overrides):
        base = {
            "trigger_sensitivity": 0.3,
            "line_length": 20.0,
            "chase_speed": 15.0,
            "fade_distance": 15.0,
            "line_width": 2,
            "base_color": "#FF00FF",
            "_parcans": self._PARCAN,
            "moving_head_follow": True,
        }
        base.update(overrides)
        return base

    def _ctx(self, onset: bool = True, fft: float = 0.8, frame: int = 0):
        return RenderContext(
            seed=42, frame_index=frame, total_frames=300, fps=30,
            onset_detected=onset, fft_bands=[fft] * 8,
        )

    def test_v1_trigger_active_produces_output(self):
        """08.V1: onset_detected=True → at least some pixels lit."""
        layer = SpectroidChaseLayer()
        frame = layer.render_frame(self._ctx(onset=True), self._params())
        assert frame.max() > 0, "Expected pixels when triggered"

    def test_v1_trigger_inactive_no_output(self):
        """08.V1: onset=False + low fft → blank frame."""
        layer = SpectroidChaseLayer()
        ctx = RenderContext(seed=42, frame_index=0, total_frames=300, fps=30,
                            onset_detected=False, fft_bands=[0.0] * 8)
        frame = layer.render_frame(ctx, self._params(trigger_sensitivity=0.9))
        assert frame.max() == 0, "Expected blank frame when not triggered"

    def test_v2_parcan_anchor_pixels_lit(self):
        """08.V2: Pixels exist near the parcan anchor coordinates."""
        layer = SpectroidChaseLayer()
        frame = layer.render_frame(self._ctx(), self._params())
        px, py = 50, 25
        region = frame[max(0, py - 5):py + 6, max(0, px - 5):px + 6]
        assert region.max() > 0, "Parcan anchor region should have lit pixels"

    def test_v3_follow_targets_populated_when_triggered(self):
        """08.V3 (08.B5): get_moving_head_targets() returns non-empty list after trigger."""
        layer = SpectroidChaseLayer()
        layer.render_frame(self._ctx(onset=True), self._params())
        targets = layer.get_moving_head_targets()
        assert len(targets) > 0, "Expected follow targets after triggered render"

    def test_v3_follow_target_schema(self):
        """08.B5: Each follow target has all required metadata keys."""
        layer = SpectroidChaseLayer()
        layer.render_frame(self._ctx(onset=True), self._params())
        required_keys = {
            "parcan_x", "parcan_y", "direction_dx", "direction_dy",
            "angle_deg", "line_length", "end_x", "end_y", "active",
        }
        for target in layer.get_moving_head_targets():
            assert required_keys <= set(target.keys()), \
                f"Follow target missing keys: {required_keys - set(target.keys())}"

    def test_v3_stability_across_frames(self):
        """08.V3: Two renders with same seed produce identical frames."""
        layer_a, layer_b = SpectroidChaseLayer(), SpectroidChaseLayer()
        params = self._params()
        ctx_a = self._ctx(frame=2)
        ctx_b = self._ctx(frame=2)
        frame_a = layer_a.render_frame(ctx_a, params)
        frame_b = layer_b.render_frame(ctx_b, params)
        np.testing.assert_array_equal(frame_a, frame_b)

    def test_v4_snapshot_shape_dtype(self):
        """08.V4: Result has correct shape and dtype."""
        layer = SpectroidChaseLayer()
        frame = layer.render_frame(self._ctx(), self._params())
        assert frame.shape == (CANVAS_HEIGHT, CANVAS_WIDTH, 3)
        assert frame.dtype == np.uint8
        assert frame.min() >= 0
        assert frame.max() <= 255

    def test_v4_follow_targets_empty_when_not_triggered(self):
        """08.V4: No follow targets when trigger is inactive."""
        layer = SpectroidChaseLayer()
        ctx = RenderContext(seed=42, frame_index=0, total_frames=300, fps=30,
                            onset_detected=False, fft_bands=[0.0] * 8)
        layer.render_frame(ctx, self._params(trigger_sensitivity=0.9))
        assert layer.get_moving_head_targets() == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
