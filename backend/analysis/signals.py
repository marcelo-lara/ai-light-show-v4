import bisect

from .schema import AnalysisIRV1, AnalysisSignals


def query_at(ir: AnalysisIRV1, time: float) -> AnalysisSignals:
    beat_phase, nearest_beat_dist = _beat_phase(ir, time)
    bar_phase = _bar_phase(ir, time)
    return AnalysisSignals(
        beat_phase=beat_phase,
        bar_phase=bar_phase,
        nearest_beat_distance=nearest_beat_dist,
        bass=_envelope_at(ir, "bass", time),
        mid=_envelope_at(ir, "mid", time),
        high=_envelope_at(ir, "high", time),
        energy=_lerp_signal(ir.energy_times, ir.energy_values, time),
    )


def _beat_phase(ir: AnalysisIRV1, t: float) -> tuple[float, float]:
    times = [b.time for b in ir.beats]
    if not times:
        return 0.0, 0.0
    idx = max(0, bisect.bisect_right(times, t) - 1)
    prev = times[idx]
    nxt = times[idx + 1] if idx + 1 < len(times) else prev + 0.5
    interval = max(nxt - prev, 1e-6)
    phase = min(max((t - prev) / interval, 0.0), 1.0)
    dist = min(abs(t - prev), abs(t - nxt))
    return float(phase), float(dist)


def _bar_phase(ir: AnalysisIRV1, t: float) -> float:
    times = [b.time for b in ir.bars]
    if not times:
        return 0.0
    idx = max(0, bisect.bisect_right(times, t) - 1)
    prev = times[idx]
    nxt = times[idx + 1] if idx + 1 < len(times) else prev + 2.0
    return float(min(max((t - prev) / max(nxt - prev, 1e-6), 0.0), 1.0))


def _envelope_at(ir: AnalysisIRV1, band: str, t: float) -> float:
    for env in ir.band_envelopes:
        if env.band == band:
            return _lerp_signal(env.times, env.values, t)
    return 0.0


def _lerp_signal(times: list[float], values: list[float], t: float) -> float:
    if not times:
        return 0.0
    idx = bisect.bisect_right(times, t) - 1
    if idx < 0:
        return float(values[0])
    if idx >= len(values) - 1:
        return float(values[-1])
    t0, t1 = times[idx], times[idx + 1]
    alpha = (t - t0) / max(t1 - t0, 1e-6)
    return float(values[idx] + alpha * (values[idx + 1] - values[idx]))
