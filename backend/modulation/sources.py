from __future__ import annotations

import math
import random as _random
from typing import Any

from analysis.schema import AnalysisSignals

_AUDIO_SOURCES = {
    "beat_phase", "bar_phase", "bass", "mid", "high", "energy", "beat_pulse",
    "nearest_beat_distance",
}


def resolve_source(
    source: str,
    signals: AnalysisSignals,
    time: float,
    seed: int,
    extra: dict[str, Any],
) -> float:
    if source in _AUDIO_SOURCES:
        return _audio(source, signals)
    if source == "lfo":
        return _lfo(
            time,
            freq=float(extra.get("lfo_freq", 1.0)),
            shape=str(extra.get("lfo_shape", "sine")),
        )
    if source == "random":
        return _seeded_random(seed + int(extra.get("random_seed", 0)))
    raise ValueError(f"Unknown modulator source: {source!r}")


def _audio(source: str, sig: AnalysisSignals) -> float:
    if source == "beat_phase":
        return sig.beat_phase
    if source == "bar_phase":
        return sig.bar_phase
    if source == "bass":
        return sig.bass
    if source == "mid":
        return sig.mid
    if source == "high":
        return sig.high
    if source == "energy":
        return sig.energy
    if source == "beat_pulse":
        return 1.0 - sig.beat_phase
    if source == "nearest_beat_distance":
        return float(min(max(sig.nearest_beat_distance, 0.0), 1.0))
    return 0.0


def _lfo(t: float, freq: float, shape: str) -> float:
    phase = (t * freq) % 1.0
    if shape == "sine":
        return (math.sin(2 * math.pi * phase) + 1.0) * 0.5
    if shape == "square":
        return 1.0 if phase < 0.5 else 0.0
    if shape == "saw":
        return phase
    return (math.sin(2 * math.pi * phase) + 1.0) * 0.5


def _seeded_random(combined_seed: int) -> float:
    rng = _random.Random(combined_seed)
    return rng.random()
