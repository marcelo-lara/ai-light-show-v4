from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from .types import LayerBase, LayerMeta

_registry: dict[str, type] = {}


def register(cls: Type["LayerBase"]) -> Type["LayerBase"]:
    _registry[cls.meta.layer_id] = cls
    return cls


def get(layer_id: str) -> type:
    if layer_id not in _registry:
        raise KeyError(f"Layer not found: {layer_id!r}")
    return _registry[layer_id]


def list_layers() -> list["LayerMeta"]:
    return [cls.meta for cls in _registry.values()]


def _load_defaults() -> None:
    from . import (  # noqa: F401
        beat_flash,
        bouncing_ball,
        gradient,
        ocean_waves,
        raindrops,
        solid,
        spectroid_chase,
        wave,
    )


_load_defaults()
