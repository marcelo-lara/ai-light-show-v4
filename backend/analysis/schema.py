from __future__ import annotations

import hashlib
from typing import Any, Literal

from pydantic import BaseModel

ANALYSIS_SCHEMA_VERSION = "1.0.0"


class BeatEvent(BaseModel):
    time: float
    confidence: float = 1.0


class BarEvent(BaseModel):
    time: float


class SectionCandidate(BaseModel):
    start: float
    end: float
    label: str
    confidence: float


class BandEnvelope(BaseModel):
    band: str
    times: list[float]
    values: list[float]


class AnalysisDiagnostics(BaseModel):
    analyzer_version: str
    analysis_duration_s: float
    confidence: float
    source_metadata: dict[str, Any] = {}


class AnalysisIRV1(BaseModel):
    schema_version: Literal[1] = 1
    analysis_id: str
    song_id: str
    duration: float
    sample_rate: int = 44100
    beats: list[BeatEvent]
    bars: list[BarEvent]
    downbeats: list[float]
    sections: list[SectionCandidate]
    band_envelopes: list[BandEnvelope]
    energy_times: list[float]
    energy_values: list[float]
    diagnostics: AnalysisDiagnostics


class AnalysisSignals(BaseModel):
    beat_phase: float
    bar_phase: float
    nearest_beat_distance: float
    bass: float
    mid: float
    high: float
    energy: float


def make_analysis_id(song_id: str) -> str:
    payload = f"{song_id}:{ANALYSIS_SCHEMA_VERSION}"
    h = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return f"{song_id}.analysis.{h}"
