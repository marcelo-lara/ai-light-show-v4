"""
Built-in Preset Definitions

Epic 06.B7-B8: Pre-defined presets including baseline migrations.
"""

from datetime import datetime
from .preset import (
    PresetDefinition,
    PresetMetadata,
    ParameterSchema,
    ParameterType,
    ParameterConstraint,
    ColorPalette,
    LayerReference,
    BlendMode,
)


def create_undersea_waves_preset() -> PresetDefinition:
    """
    Epic 06.B7: Undersea Waves preset.
    
    Three layered sine waves moving left to right, parcan-restricted,
    with configurable base color. Wave speed responds to beat timing,
    intensity modulates with FFT band changes.
    """
    return PresetDefinition(
        metadata=PresetMetadata(
            preset_id="undersea_waves",
            version="1.0",
            label="Undersea Waves",
            tags=["wave", "water", "parcan", "beat-reactive", "fft-reactive"],
            description="Three layered sine waves moving left to right with beat and FFT modulation",
            author="AI Light Show",
        ),
        parameters={
            "base_color": ParameterSchema(
                name="base_color",
                type=ParameterType.COLOR,
                label="Base Color",
                description="Primary wave color",
                default_value="#0000FF",
                ui_group="Color",
            ),
            "wave_speed_base": ParameterSchema(
                name="wave_speed_base",
                type=ParameterType.FLOAT,
                label="Wave Speed (Base)",
                description="Baseline wave speed",
                default_value=1.0,
                constraint=ParameterConstraint(min_value=0.1, max_value=5.0, step_size=0.1),
                ui_group="Wave",
            ),
            "wave_amplitude": ParameterSchema(
                name="wave_amplitude",
                type=ParameterType.FLOAT,
                label="Wave Amplitude",
                description="Vertical wave amplitude",
                default_value=1.0,
                constraint=ParameterConstraint(min_value=0.1, max_value=2.0, step_size=0.1),
                ui_group="Wave",
            ),
            "glitter_intensity": ParameterSchema(
                name="glitter_intensity",
                type=ParameterType.FLOAT,
                label="Glitter (FFT-Reactive)",
                description="Glitter effect intensity driven by FFT bands",
                default_value=0.5,
                constraint=ParameterConstraint(min_value=0.0, max_value=1.0, step_size=0.1),
                ui_group="Effects",
            ),
        },
        palette=ColorPalette(
            name="ocean",
            colors={
                "deep": "#001a4d",
                "mid": "#0033cc",
                "light": "#0066ff",
                "bright": "#00FFFF",
            },
            description="Ocean color palette",
        ),
        layers=[
            LayerReference(
                layer_id="wave",
                label="Wave Layer 1 (Slow)",
                order=0,
                blend_mode=BlendMode.ADD,
                opacity=0.8,
                params={
                    "speed": 0.8,
                    "wavelength": 30,
                    "amplitude": 0.8,
                },
            ),
            LayerReference(
                layer_id="wave",
                label="Wave Layer 2 (Medium)",
                order=1,
                blend_mode=BlendMode.ADD,
                opacity=0.6,
                params={
                    "speed": 1.2,
                    "wavelength": 20,
                    "amplitude": 0.6,
                },
            ),
            LayerReference(
                layer_id="wave",
                label="Wave Layer 3 (Fast)",
                order=2,
                blend_mode=BlendMode.ADD,
                opacity=0.4,
                params={
                    "speed": 1.8,
                    "wavelength": 15,
                    "amplitude": 0.4,
                },
            ),
        ],
        default_blend_mode=BlendMode.ADD,
    )


def create_undersea_pulse_01_preset() -> PresetDefinition:
    """
    Epic 06.B8: Baseline Pulse preset.
    
    Migrates current wave+pulse look as a preset.
    Combines wave layers with radial pulse for a pulsing wave effect.
    """
    return PresetDefinition(
        metadata=PresetMetadata(
            preset_id="undersea_pulse_01",
            version="1.0",
            label="Undersea Pulse",
            tags=["wave", "pulse", "water", "baseline"],
            description="Baseline wave and pulse combination",
            author="AI Light Show",
        ),
        parameters={
            "base_color": ParameterSchema(
                name="base_color",
                type=ParameterType.COLOR,
                label="Base Color",
                description="Primary color",
                default_value="#0000FF",
                ui_group="Color",
            ),
            "wave_speed": ParameterSchema(
                name="wave_speed",
                type=ParameterType.FLOAT,
                label="Wave Speed",
                default_value=1.0,
                constraint=ParameterConstraint(min_value=0.1, max_value=5.0),
                ui_group="Wave",
            ),
            "pulse_speed": ParameterSchema(
                name="pulse_speed",
                type=ParameterType.FLOAT,
                label="Pulse Speed",
                default_value=10.0,
                constraint=ParameterConstraint(min_value=1.0, max_value=50.0),
                ui_group="Pulse",
            ),
        },
        layers=[
            LayerReference(
                layer_id="wave",
                label="Base Wave",
                order=0,
                blend_mode=BlendMode.ALPHA,
                opacity=0.7,
                params={
                    "speed": 1.0,
                    "wavelength": 25,
                    "amplitude": 1.0,
                },
            ),
            LayerReference(
                layer_id="radial_pulse",
                label="Center Pulse",
                order=1,
                blend_mode=BlendMode.ADD,
                opacity=0.8,
                params={
                    "center_x": 50,
                    "center_y": 25,
                    "pulse_speed": 10.0,
                    "pulse_radius": 15.0,
                    "decay": 0.95,
                },
            ),
        ],
    )


def get_builtin_presets() -> dict:
    """
    Get all built-in presets.
    
    Returns:
        Dict mapping preset IDs to PresetDefinition objects.
    """
    presets = [
        create_undersea_waves_preset(),
        create_undersea_pulse_01_preset(),
    ]
    
    return {
        f"{p.metadata.preset_id}:{p.metadata.version}": p
        for p in presets
    }
