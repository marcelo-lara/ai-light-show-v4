import time as _time

import numpy as np

from .schema import (
    ANALYSIS_SCHEMA_VERSION,
    AnalysisDiagnostics,
    AnalysisIRV1,
    BandEnvelope,
    BarEvent,
    BeatEvent,
    make_analysis_id,
)

_SR = 44100
_WIN = 1024
_HOP = 512
_BANDS = [("bass", 20, 300), ("mid", 300, 5000), ("high", 5000, 20000)]


def analyze(audio_path: str, song_id: str) -> AnalysisIRV1:
    t0 = _time.monotonic()
    import essentia.standard as es

    audio = es.MonoLoader(filename=audio_path, sampleRate=_SR)()
    duration = len(audio) / _SR
    beats, bpm, conf = _extract_beats(audio, es)
    bars = _beats_to_bars(beats)
    downbeats = [bars[i].time for i in range(0, len(bars), 4)] if bars else []
    band_envs = _extract_band_envelopes(audio, es)
    e_times, e_vals = _extract_energy(audio, es)

    return AnalysisIRV1(
        analysis_id=make_analysis_id(song_id),
        song_id=song_id,
        duration=duration,
        beats=beats,
        bars=bars,
        downbeats=downbeats,
        sections=[],
        band_envelopes=band_envs,
        energy_times=e_times,
        energy_values=e_vals,
        diagnostics=AnalysisDiagnostics(
            analyzer_version=ANALYSIS_SCHEMA_VERSION,
            analysis_duration_s=_time.monotonic() - t0,
            confidence=conf,
        ),
    )


def _extract_beats(audio: np.ndarray, es) -> tuple[list[BeatEvent], float, float]:
    bpm, beat_times, confidence, _, _ = es.RhythmExtractor2013(method="multifeature")(audio)
    beats = [BeatEvent(time=float(t), confidence=float(confidence)) for t in beat_times]
    return beats, float(bpm), float(confidence)


def _beats_to_bars(beats: list[BeatEvent], bpb: int = 4) -> list[BarEvent]:
    return [BarEvent(time=beats[i].time) for i in range(0, len(beats), bpb)]


def _extract_band_envelopes(audio: np.ndarray, es) -> list[BandEnvelope]:
    spectrum = es.Spectrum(size=_WIN)
    window = es.Windowing(type="hann", size=_WIN)
    freq_res = _SR / _WIN
    accum: dict[str, list[float]] = {n: [] for n, *_ in _BANDS}
    frames = list(es.FrameGenerator(audio, frameSize=_WIN, hopSize=_HOP, startFromZero=True))
    times = [i * _HOP / _SR for i in range(len(frames))]
    for frame in frames:
        spec = spectrum(window(frame))
        for name, lo, hi in _BANDS:
            lo_i = max(0, int(lo / freq_res))
            hi_i = min(len(spec), int(hi / freq_res))
            accum[name].append(float(np.sqrt(np.mean(spec[lo_i:hi_i] ** 2 + 1e-12))))
    result = []
    for name, *_ in _BANDS:
        vals = np.array(accum[name])
        mx = vals.max()
        if mx > 0:
            vals = vals / mx
        result.append(BandEnvelope(band=name, times=times, values=list(vals.astype(float))))
    return result


def _extract_energy(audio: np.ndarray, es) -> tuple[list[float], list[float]]:
    rms = es.RMS()
    vals, times = [], []
    for i, frame in enumerate(es.FrameGenerator(audio, frameSize=_WIN, hopSize=_HOP, startFromZero=True)):
        vals.append(float(rms(frame)))
        times.append(i * _HOP / _SR)
    arr = np.array(vals)
    mx = arr.max()
    if mx > 0:
        arr = arr / mx
    return times, list(arr.astype(float))
