"""
Validation Tests for Phase 04: Timeline and Direction

Tests for:
- Epic 09: Timeline Director (scenes, auto-generation, overrides)
- Epic 10: Transition System (types, alignment, determinism)
"""

import pytest
from datetime import datetime
import numpy as np

from app.timeline import (
    Scene, SceneTimeline, TimelineGenerator, AlignmentType, AutomationCurve,
    ControlPoint, InterpolationType, merge_scene_override,
)
from app.transitions import (
    Transition, HardCutTransition, CrossfadeTransition, BeatFlashCutTransition,
    TransitionType, TransitionAligner, TransitionDebugInfo, create_transition_debug_info,
)


class TestSceneModel:
    """Tests for Epic 09.B1: Scene model."""
    
    def test_scene_creation(self):
        """Test basic scene creation."""
        scene = Scene(
            scene_id="scene_0",
            start_time=0.0,
            end_time=10.0,
            preset_id="undersea_waves",
            seed=42,
        )
        
        assert scene.scene_id == "scene_0"
        assert scene.start_time == 0.0
        assert scene.end_time == 10.0
        assert scene.preset_id == "undersea_waves"
        assert scene.seed == 42
        assert scene.intensity == 1.0
    
    def test_scene_with_musical_alignment(self):
        """Test scene with beat/bar alignment."""
        scene = Scene(
            scene_id="scene_0",
            start_time=0.0,
            end_time=10.0,
            start_beat=0,
            start_bar=0,
            preset_id="undersea_waves",
            seed=42,
        )
        
        assert scene.start_beat == 0
        assert scene.start_bar == 0
    
    def test_scene_get_intensity_at_time(self):
        """Test intensity calculation at specific time."""
        scene = Scene(
            scene_id="scene_0",
            start_time=5.0,
            end_time=15.0,
            preset_id="undersea_waves",
            intensity=0.8,
        )
        
        # Before scene
        assert scene.get_intensity_at_time(0.0) == 0.0
        
        # Within scene
        assert scene.get_intensity_at_time(10.0) == 0.8
        
        # After scene
        assert scene.get_intensity_at_time(20.0) == 0.0
    
    def test_scene_with_intensity_automation(self):
        """Test scene with intensity automation curve."""
        automation = AutomationCurve(
            name="intensity",
            interpolation=InterpolationType.LINEAR,
            control_points=[
                ControlPoint(time=0.0, value=0.0),
                ControlPoint(time=5.0, value=1.0),
                ControlPoint(time=10.0, value=0.0),
            ],
        )
        
        scene = Scene(
            scene_id="scene_0",
            start_time=0.0,
            end_time=10.0,
            preset_id="undersea_waves",
            intensity=1.0,
            intensity_automation=automation,
        )
        
        # Intensity ramps from 0 to 1 then back to 0
        assert scene.get_intensity_at_time(0.0) == 0.0  # start of ramp
        assert scene.get_intensity_at_time(5.0) == 1.0  # peak
        assert scene.get_intensity_at_time(10.0) == 0.0  # end of ramp
    
    def test_scene_auto_generated_flag(self):
        """Test auto-generated flag."""
        auto_scene = Scene(
            scene_id="scene_auto",
            start_time=0.0,
            end_time=10.0,
            preset_id="undersea_waves",
            is_auto_generated=True,
        )
        
        manual_scene = Scene(
            scene_id="scene_manual",
            start_time=0.0,
            end_time=10.0,
            preset_id="undersea_pulse_01",
            is_manual_override=True,
        )
        
        assert auto_scene.is_auto_generated
        assert manual_scene.is_manual_override


class TestAutomationCurve:
    """Tests for automation curves (intensity and parameter automation)."""
    
    def test_automation_curve_linear_interpolation(self):
        """Test linear interpolation."""
        curve = AutomationCurve(
            name="test_param",
            interpolation=InterpolationType.LINEAR,
            control_points=[
                ControlPoint(time=0.0, value=0.0),
                ControlPoint(time=1.0, value=1.0),
            ],
        )
        
        assert curve.evaluate(0.0) == 0.0
        assert curve.evaluate(0.5) == pytest.approx(0.5)
        assert curve.evaluate(1.0) == 1.0
    
    def test_automation_curve_ease_in(self):
        """Test ease-in interpolation."""
        curve = AutomationCurve(
            name="test_param",
            interpolation=InterpolationType.EASE_IN,
            control_points=[
                ControlPoint(time=0.0, value=0.0),
                ControlPoint(time=1.0, value=1.0),
            ],
        )
        
        # Ease-in: t^2, so at t=0.5, value ≈ 0.25
        assert curve.evaluate(0.5) < 0.5
    
    def test_automation_curve_multiple_points(self):
        """Test curve with multiple control points."""
        curve = AutomationCurve(
            name="test_param",
            interpolation=InterpolationType.LINEAR,
            control_points=[
                ControlPoint(time=0.0, value=0.0),
                ControlPoint(time=1.0, value=1.0),
                ControlPoint(time=2.0, value=0.5),
            ],
        )
        
        assert curve.evaluate(0.0) == 0.0
        assert curve.evaluate(1.0) == 1.0
        assert curve.evaluate(2.0) == 0.5
        assert curve.evaluate(1.5) == pytest.approx(0.75)


class TestSceneTimeline:
    """Tests for Epic 09: Timeline model."""
    
    def test_timeline_creation(self):
        """Test basic timeline creation."""
        scenes = [
            Scene(
                scene_id="scene_0",
                start_time=0.0,
                end_time=10.0,
                preset_id="undersea_waves",
            ),
            Scene(
                scene_id="scene_1",
                start_time=10.0,
                end_time=20.0,
                preset_id="undersea_pulse_01",
            ),
        ]
        
        timeline = SceneTimeline(
            timeline_id="timeline_0",
            song_id="song_0",
            duration=20.0,
            scenes=scenes,
        )
        
        assert timeline.timeline_id == "timeline_0"
        assert timeline.song_id == "song_0"
        assert len(timeline.scenes) == 2
    
    def test_timeline_get_scene_at_time(self):
        """Test retrieval of active scene at time."""
        timeline = SceneTimeline(
            timeline_id="timeline_0",
            song_id="song_0",
            duration=30.0,
            scenes=[
                Scene(
                    scene_id="scene_0",
                    start_time=0.0,
                    end_time=10.0,
                    preset_id="undersea_waves",
                ),
                Scene(
                    scene_id="scene_1",
                    start_time=10.0,
                    end_time=20.0,
                    preset_id="undersea_pulse_01",
                ),
            ],
        )
        
        # Time in first scene
        scene = timeline.get_scene_at_time(5.0)
        assert scene is not None
        assert scene.scene_id == "scene_0"
        
        # Time in second scene
        scene = timeline.get_scene_at_time(15.0)
        assert scene is not None
        assert scene.scene_id == "scene_1"
        
        # Time outside timeline
        scene = timeline.get_scene_at_time(25.0)
        assert scene is None
    
    def test_timeline_validate_chronological(self):
        """Test timeline validation for chronological order."""
        # Invalid: overlapping scenes
        invalid_timeline = SceneTimeline(
            timeline_id="timeline_0",
            song_id="song_0",
            duration=20.0,
            scenes=[
                Scene(
                    scene_id="scene_0",
                    start_time=0.0,
                    end_time=15.0,
                    preset_id="undersea_waves",
                ),
                Scene(
                    scene_id="scene_1",
                    start_time=10.0,  # Overlaps with scene 0
                    end_time=20.0,
                    preset_id="undersea_pulse_01",
                ),
            ],
        )
        
        is_valid, errors = invalid_timeline.validate()
        assert not is_valid
        assert len(errors) > 0


class TestTimelineGeneratorFromSections:
    """Tests for Epic 09.B2: Auto-generate timeline from sections."""
    
    def test_generate_from_sections(self):
        """Test timeline generation from sections."""
        generator = TimelineGenerator(available_presets=["preset_a", "preset_b"])
        
        sections = [
            {"start": 0.0, "end": 10.0, "label": "Intro"},
            {"start": 10.0, "end": 20.0, "label": "Verse"},
            {"start": 20.0, "end": 30.0, "label": "Chorus"},
        ]
        
        timeline = generator.generate_from_sections(
            song_id="song_0",
            duration=30.0,
            sections=sections,
            base_seed=42,
        )
        
        assert len(timeline.scenes) == 3
        assert timeline.auto_generated
        assert timeline.generation_method == "sections"
        
        # Check scenes
        assert timeline.scenes[0].start_time == 0.0
        assert timeline.scenes[1].start_time == 10.0
        assert timeline.scenes[2].start_time == 20.0
        
        # Check preset cycling
        assert timeline.scenes[0].preset_id == "preset_a"
        assert timeline.scenes[1].preset_id == "preset_b"
        assert timeline.scenes[2].preset_id == "preset_a"
    
    def test_generate_from_sections_deterministic_seeds(self):
        """Test that generated seeds are deterministic."""
        generator = TimelineGenerator(available_presets=["preset_a"])
        
        sections = [
            {"start": 0.0, "end": 10.0},
            {"start": 10.0, "end": 20.0},
        ]
        
        timeline1 = generator.generate_from_sections(
            song_id="song_0",
            duration=20.0,
            sections=sections,
            base_seed=42,
        )
        
        timeline2 = generator.generate_from_sections(
            song_id="song_0",
            duration=20.0,
            sections=sections,
            base_seed=42,
        )
        
        # Seeds should match for same input
        for s1, s2 in zip(timeline1.scenes, timeline2.scenes):
            assert s1.seed == s2.seed


class TestTimelineGeneratorFromPhrases:
    """Tests for Epic 09.B3: Auto-generate from phrases."""
    
    def test_generate_from_phrases(self):
        """Test timeline generation from phrases."""
        generator = TimelineGenerator(available_presets=["preset_a", "preset_b"])
        
        phrases = [
            {"start": 0.0, "end": 5.0},
            {"start": 5.0, "end": 10.0},
            {"start": 10.0, "end": 15.0},
        ]
        
        timeline = generator.generate_from_phrases(
            song_id="song_0",
            duration=15.0,
            phrases=phrases,
            base_seed=42,
        )
        
        assert len(timeline.scenes) == 3
        assert timeline.generation_method == "phrases"


class TestTimelineGeneratorFromBeats:
    """Tests for Epic 09.B3: Auto-generate from beats."""
    
    def test_generate_from_beats(self):
        """Test timeline generation from beat grouping."""
        beat_times = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        
        generator = TimelineGenerator(available_presets=["preset_a", "preset_b"])
        
        timeline = generator.generate_from_beats(
            song_id="song_0",
            duration=4.0,
            beat_times=beat_times,
            scenes_per_beat_group=2,
            base_seed=42,
        )
        
        assert len(timeline.scenes) == 4  # 8 beats / 2 per group
        assert timeline.generation_method == "beats"


class TestSceneOverride:
    """Tests for Epic 09.B4: Scene overrides."""
    
    def test_merge_scene_override(self):
        """Test merging auto-generated with manual override."""
        auto_scene = Scene(
            scene_id="scene_0",
            start_time=0.0,
            end_time=10.0,
            preset_id="preset_a",
            seed=42,
        )
        
        override = Scene(
            scene_id="scene_0",
            start_time=0.0,
            end_time=10.0,
            preset_id="preset_b",  # Override preset
            seed=0,
        )
        
        merged = merge_scene_override(auto_scene, override)
        
        assert merged.preset_id == "preset_b"
        assert merged.is_manual_override
        assert merged.seed == 42  # Seed not changed because override.seed is 0 (default)


class TestTransitionModel:
    """Tests for Epic 10.B1: Transition model."""
    
    def test_transition_creation(self):
        """Test basic transition creation."""
        transition = Transition(
            transition_id="trans_0",
            from_scene_id="scene_0",
            to_scene_id="scene_1",
            type=TransitionType.HARD_CUT,
            start_time=10.0,
        )
        
        assert transition.transition_id == "trans_0"
        assert transition.type == TransitionType.HARD_CUT
        assert transition.duration == 0.0
    
    def test_transition_get_progress(self):
        """Test transition progress calculation."""
        transition = Transition(
            transition_id="trans_0",
            from_scene_id="scene_0",
            to_scene_id="scene_1",
            type=TransitionType.CROSSFADE,
            start_time=10.0,
            duration=2.0,
        )
        
        # Before transition
        progress = transition.get_transition_progress(9.0)
        assert progress == -1
        
        # During transition
        progress = transition.get_transition_progress(11.0)
        assert progress == pytest.approx(0.5)
        
        # After transition
        progress = transition.get_transition_progress(13.0)
        assert progress == -1


class TestHardCutTransition:
    """Tests for Epic 10.B2: Hard cut transitions."""
    
    def test_hard_cut_render(self):
        """Test hard cut produces new frame."""
        transition = HardCutTransition(
            transition_id="trans_0",
            from_scene_id="scene_0",
            to_scene_id="scene_1",
            start_time=10.0,
        )
        
        frame_from = np.zeros((50, 100, 3), dtype=np.uint8)
        frame_to = np.ones((50, 100, 3), dtype=np.uint8) * 255
        
        result = transition.render_transition_frame(frame_from, frame_to, 0.5)
        
        # Hard cut always returns frame_to
        assert np.array_equal(result, frame_to)


class TestCrossfadeTransition:
    """Tests for Epic 10.B3: Crossfade transitions."""
    
    def test_crossfade_render(self):
        """Test crossfade blends frames."""
        transition = CrossfadeTransition(
            transition_id="trans_0",
            from_scene_id="scene_0",
            to_scene_id="scene_1",
            start_time=10.0,
            duration=1.0,
        )
        
        frame_from = np.zeros((50, 100, 3), dtype=np.uint8)
        frame_to = np.ones((50, 100, 3), dtype=np.uint8) * 255
        
        # At 50% progress, should blend 50/50
        result = transition.render_transition_frame(frame_from, frame_to, 0.5)
        
        # Result should be approximately 127-128 (50% blend)
        expected = np.ones((50, 100, 3), dtype=np.uint8) * 127
        assert np.allclose(result, expected, atol=1)


class TestBeatFlashCutTransition:
    """Tests for Epic 10.B4: Beat flash cut transitions."""
    
    def test_beat_flash_render_flash_phase(self):
        """Test flash phase of beat flash cut."""
        transition = BeatFlashCutTransition(
            transition_id="trans_0",
            from_scene_id="scene_0",
            to_scene_id="scene_1",
            start_time=10.0,
            duration=0.2,
        )
        
        frame_from = np.zeros((50, 100, 3), dtype=np.uint8)
        frame_to = np.ones((50, 100, 3), dtype=np.uint8) * 100
        
        # Flash phase (progress < 0.5)
        result = transition.render_transition_frame(frame_from, frame_to, 0.25)
        
        # Should contain white (255) and some of frame_to (100)
        assert result.max() > 100


class TestTransitionAligner:
    """Tests for Epic 10.B5: Beat-aware alignment."""
    
    def test_align_to_beat(self):
        """Test alignment to beat boundaries."""
        beat_times = [0.0, 0.5, 1.0, 1.5, 2.0]
        
        aligned = TransitionAligner.align_to_beat(0.7, beat_times)
        assert aligned == 0.5 or aligned == 1.0
    
    def test_align_to_bar(self):
        """Test alignment to bar boundaries."""
        beat_times = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        
        aligned = TransitionAligner.align_to_bar(1.2, beat_times, beats_per_bar=2)
        assert aligned in [0.0, 1.0, 2.0]


class TestTransitionDebugInfo:
    """Tests for Epic 10.B7: Transition debug information."""
    
    def test_create_debug_info(self):
        """Test debug info creation."""
        transition = Transition(
            transition_id="trans_0",
            from_scene_id="scene_0",
            to_scene_id="scene_1",
            type=TransitionType.CROSSFADE,
            start_time=10.0,
            duration=1.0,
            start_beat=20,
        )
        
        debug_info = create_transition_debug_info(transition, current_frame_time=10.5)
        
        assert debug_info.transition_id == "trans_0"
        assert debug_info.type == TransitionType.CROSSFADE
        assert debug_info.progress_at_sample == pytest.approx(0.5)


class TestMultiSceneRender:
    """Tests for Epic 09.V1: Multi-scene render."""
    
    def test_multi_scene_timeline_generation(self):
        """Prove timeline can be generated with 3+ scenes."""
        generator = TimelineGenerator(available_presets=["preset_a", "preset_b"])
        
        sections = [
            {"start": 0.0, "end": 10.0},
            {"start": 10.0, "end": 20.0},
            {"start": 20.0, "end": 30.0},
            {"start": 30.0, "end": 40.0},
        ]
        
        timeline = generator.generate_from_sections(
            song_id="song_0",
            duration=40.0,
            sections=sections,
        )
        
        assert len(timeline.scenes) >= 3
        assert all(scene.preset_id in ["preset_a", "preset_b"] for scene in timeline.scenes)
    
    def test_timeline_with_different_presets_per_scene(self):
        """Prove each scene uses different preset."""
        generator = TimelineGenerator(
            available_presets=["preset_a", "preset_b", "preset_c"]
        )
        
        sections = [
            {"start": 0.0, "end": 10.0},
            {"start": 10.0, "end": 20.0},
            {"start": 20.0, "end": 30.0},
        ]
        
        timeline = generator.generate_from_sections(
            song_id="song_0",
            duration=30.0,
            sections=sections,
        )
        
        assert timeline.scenes[0].preset_id == "preset_a"
        assert timeline.scenes[1].preset_id == "preset_b"
        assert timeline.scenes[2].preset_id == "preset_c"


class TestSceneAlignment:
    """Tests for Epic 09.V2: Scene alignment."""
    
    def test_scenes_align_to_section_boundaries(self):
        """Prove auto scenes align to section boundaries."""
        generator = TimelineGenerator()
        
        sections = [
            {"start": 0.0, "end": 10.0},
            {"start": 10.0, "end": 20.0},
        ]
        
        timeline = generator.generate_from_sections(
            song_id="song_0",
            duration=20.0,
            sections=sections,
        )
        
        # Scenes should match section boundaries
        assert timeline.scenes[0].start_time == 0.0
        assert timeline.scenes[0].end_time == 10.0
        assert timeline.scenes[1].start_time == 10.0
    
    def test_scenes_can_align_to_beats(self):
        """Prove beat alignment works."""
        beat_times = [0.0, 0.5, 1.0, 1.5, 2.0]
        generator = TimelineGenerator()
        
        timeline = generator.generate_from_beats(
            song_id="song_0",
            duration=2.5,
            beat_times=beat_times,
            scenes_per_beat_group=2,
        )
        
        assert len(timeline.scenes) > 0
        for scene in timeline.scenes:
            # Scenes should start at or near beat times
            assert any(abs(scene.start_time - bt) < 0.01 for bt in beat_times + [b + 0.5 for b in beat_times])


class TestDeterminism:
    """Tests for Epic 10.V1: Deterministic transitions."""
    
    def test_crossfade_determinism(self):
        """Prove crossfade is reproducible."""
        transition = CrossfadeTransition(
            transition_id="trans_0",
            from_scene_id="scene_0",
            to_scene_id="scene_1",
            start_time=10.0,
            duration=1.0,
        )
        
        frame_from = np.ones((50, 100, 3), dtype=np.uint8) * 100
        frame_to = np.ones((50, 100, 3), dtype=np.uint8) * 200
        
        result1 = transition.render_transition_frame(frame_from, frame_to, 0.5)
        result2 = transition.render_transition_frame(frame_from, frame_to, 0.5)
        
        assert np.array_equal(result1, result2)


class TestTransitionDuration:
    """Tests for Epic 10.V2: Transition duration."""
    
    def test_transition_duration_honored(self):
        """Prove transition duration is respected."""
        transition = Transition(
            transition_id="trans_0",
            from_scene_id="scene_0",
            to_scene_id="scene_1",
            type=TransitionType.CROSSFADE,
            start_time=10.0,
            duration=2.0,
        )
        
        # Progress should go from 0 to 1 over 2 seconds
        p1 = transition.get_transition_progress(10.0)
        p2 = transition.get_transition_progress(11.0)
        p3 = transition.get_transition_progress(12.0)
        
        assert p1 == pytest.approx(0.0)
        assert p2 == pytest.approx(0.5)
        assert p3 == pytest.approx(1.0)
    
    def test_hard_cut_zero_duration(self):
        """Prove hard cut is instant."""
        transition = HardCutTransition(
            transition_id="trans_0",
            from_scene_id="scene_0",
            to_scene_id="scene_1",
            start_time=10.0,
        )
        
        assert transition.duration == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
