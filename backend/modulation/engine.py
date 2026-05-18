from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from analysis.schema import AnalysisSignals

from .ops import apply_ops
from .sources import resolve_source


class ModulatorBinding(BaseModel):
    source: str
    lfo_freq: float = 1.0
    lfo_shape: str = "sine"
    random_seed: int = 0
    ops: list[dict[str, Any]] = []


class ModulatorEngine:
    def __init__(self) -> None:
        self._state: dict[str, dict] = {}

    def resolve(
        self,
        mod_id: str,
        binding: ModulatorBinding,
        signals: AnalysisSignals,
        time: float,
        seed: int,
    ) -> float:
        state = self._state.setdefault(mod_id, {})
        extra = {
            "lfo_freq": binding.lfo_freq,
            "lfo_shape": binding.lfo_shape,
            "random_seed": binding.random_seed,
        }
        raw = resolve_source(binding.source, signals, time, seed, extra)
        return apply_ops(raw, binding.ops, state)

    def resolve_all(
        self,
        bindings: dict[str, ModulatorBinding],
        signals: AnalysisSignals,
        time: float,
        seed: int,
    ) -> dict[str, float]:
        return {
            mod_id: self.resolve(mod_id, b, signals, time, seed)
            for mod_id, b in bindings.items()
        }
