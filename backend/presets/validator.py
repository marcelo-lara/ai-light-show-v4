from __future__ import annotations

from pydantic import ValidationError

from shaders.registry import get as get_layer

from .schema import PresetV1

_MAX_REGISTERS = 32


class PresetValidationError(Exception):
    pass


def validate_preset(raw: dict) -> PresetV1:
    try:
        preset = PresetV1.model_validate(raw)
    except ValidationError as exc:
        raise PresetValidationError(str(exc)) from exc

    if len(preset.registers) > _MAX_REGISTERS:
        raise PresetValidationError(
            f"Too many registers: {len(preset.registers)} > {_MAX_REGISTERS}"
        )

    for layer in preset.layers:
        try:
            get_layer(layer.shader)
        except KeyError:
            raise PresetValidationError(
                f"Layer '{layer.id}' references unknown shader: {layer.shader!r}"
            )

    for param in preset.params:
        if param.min is not None and param.max is not None:
            if param.min > param.max:
                raise PresetValidationError(
                    f"Param '{param.id}': min ({param.min}) > max ({param.max})"
                )

    return preset
