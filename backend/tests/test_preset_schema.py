import pytest

from presets.loader import load_preset, list_preset_ids
from presets.schema import PresetV1
from presets.validator import PresetValidationError, validate_preset


def test_bouncing_ball_reference_loads():
    p = load_preset("bouncing_ball_reference_v1")
    assert isinstance(p, PresetV1)
    assert p.preset_id == "bouncing_ball_reference_v1"
    assert len(p.layers) == 1
    assert p.layers[0].shader == "bouncing_ball"


def test_undersea_pulse_loads():
    p = load_preset("undersea_pulse_01")
    assert p.preset_id == "undersea_pulse_01"
    assert len(p.layers) == 3


def test_list_preset_ids_includes_known():
    ids = list_preset_ids()
    assert "bouncing_ball_reference_v1" in ids
    assert "undersea_pulse_01" in ids


def test_valid_preset_passes_validation():
    raw = {
        "schema_version": "1.0",
        "preset_id": "test",
        "display": {"name": "Test", "tags": []},
        "layers": [{"id": "l1", "shader": "solid", "params": {}}],
    }
    preset = validate_preset(raw)
    assert preset.preset_id == "test"


def test_invalid_schema_version_fails():
    raw = {
        "schema_version": "2.0",
        "preset_id": "test",
        "display": {"name": "Test", "tags": []},
        "layers": [],
    }
    with pytest.raises(PresetValidationError):
        validate_preset(raw)


def test_unknown_shader_fails():
    raw = {
        "schema_version": "1.0",
        "preset_id": "test",
        "display": {"name": "Test"},
        "layers": [{"id": "l1", "shader": "does_not_exist"}],
    }
    with pytest.raises(PresetValidationError, match="unknown shader"):
        validate_preset(raw)


def test_too_many_registers_fails():
    raw = {
        "schema_version": "1.0",
        "preset_id": "test",
        "display": {"name": "Test"},
        "layers": [],
        "registers": [{"id": f"r{i}"} for i in range(33)],
    }
    with pytest.raises(PresetValidationError, match="registers"):
        validate_preset(raw)


def test_param_inverted_bounds_fails():
    raw = {
        "schema_version": "1.0",
        "preset_id": "test",
        "display": {"name": "Test"},
        "layers": [],
        "params": [{"id": "x", "type": "float", "default": 0.5, "min": 1.0, "max": 0.0}],
    }
    with pytest.raises(PresetValidationError, match="min.*max"):
        validate_preset(raw)


def test_missing_preset_raises():
    with pytest.raises(FileNotFoundError):
        load_preset("does_not_exist_preset_xyz")
