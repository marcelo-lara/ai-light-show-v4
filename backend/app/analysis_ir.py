"""
Analysis IR (Intermediate Representation)

Epic 03: Analysis IR
Defines a versioned schema for audio analysis data consumed by the render system,
plus a cache with schema-based invalidation and a timestamp query helper.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Bump this string whenever the analysis schema changes in a breaking way.
# AnalysisCache uses it to invalidate stale entries (Epic 03.B1).
ANALYSIS_SCHEMA_VERSION = "1.0"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class BandEnvelope(BaseModel):
    """
    Epic 03.B4: Smoothed per-band energy envelope.

    ``values`` is a list of normalised (0-1) energy samples, one per analysis
    frame at ``sample_rate_fps``.
    """

    band_index: int = Field(..., description="FFT band index (0 = sub-bass, …)")
    values: List[float] = Field(
        default_factory=list,
        description="Smoothed band energy at each analysis frame, normalised 0-1",
    )
    sample_rate_fps: float = Field(30.0, description="Analysis frames per second")


class SectionCandidate(BaseModel):
    """
    Epic 03.B6: Musical structure candidate (downbeat, phrase, or section boundary).
    """

    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    type: str = Field(..., description="One of: downbeat, phrase, section")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score 0-1")
    label: Optional[str] = Field(None, description="Human-readable label, if known")


class AnalysisDiagnostics(BaseModel):
    """
    Epic 03.B7: Diagnostic metadata exposed alongside the analysis result.

    Provides confidence scores, analyzer provenance, and arbitrary debug stats
    so downstream tooling can audit analysis quality.
    """

    analyzer_version: str = Field(..., description="Version string of the analyzer")
    analysis_schema_version: str = Field(
        ANALYSIS_SCHEMA_VERSION,
        description="Schema version this analysis was produced with",
    )
    beat_confidence: float = Field(
        0.0, ge=0.0, le=1.0, description="Overall beat-tracking confidence"
    )
    source_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary key/value provenance from the analyzer",
    )
    debug_stats: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary key/value debug counters",
    )


# ---------------------------------------------------------------------------
# Core schema
# ---------------------------------------------------------------------------


class AnalysisIR(BaseModel):
    """
    Epic 03.B1: Versioned audio analysis IR consumed by the render system.

    All frame-rate arrays (``beat_phase``, ``bar_phase``, ``global_energy``, …)
    have one entry per analysis frame at ``fps`` frames per second and are
    aligned by index: entry ``i`` corresponds to time ``i / fps``.

    The ``schema_version`` field allows ``AnalysisCache`` to detect and discard
    entries produced by an older schema (Epic 03.B1 cache invalidation).
    """

    schema_version: str = Field(
        ANALYSIS_SCHEMA_VERSION,
        description="Schema version — cache entries with older versions are invalidated",
    )
    analysis_id: str = Field(..., description="Unique, stable identifier for this analysis")
    song_id: str = Field(..., description="Source song identifier")
    duration: float = Field(..., description="Song duration in seconds")
    fps: float = Field(30.0, description="Analysis sampling rate (frames per second)")

    # Epic 03.B2: Beat timing signals
    beat_times: List[float] = Field(
        default_factory=list,
        description="Absolute beat onset times in seconds",
    )
    beat_phase: List[float] = Field(
        default_factory=list,
        description="Beat phase 0-1 at each analysis frame (Epic 03.B2)",
    )
    nearest_beat_distance: List[float] = Field(
        default_factory=list,
        description="Signed distance to nearest beat in seconds (Epic 03.B2)",
    )

    # Epic 03.B3: Bar timing signals
    bar_times: List[float] = Field(
        default_factory=list,
        description="Absolute bar onset times in seconds",
    )
    bar_phase: List[float] = Field(
        default_factory=list,
        description="Bar phase 0-1 at each analysis frame (Epic 03.B3)",
    )

    # Epic 03.B4: Smoothed envelopes
    band_envelopes: List[BandEnvelope] = Field(
        default_factory=list,
        description="Smoothed per-band energy envelopes (Epic 03.B4)",
    )

    # Epic 03.B5: Global energy
    global_energy: List[float] = Field(
        default_factory=list,
        description="Normalised global energy 0-1 at each analysis frame (Epic 03.B5)",
    )

    # Epic 03.B6: Musical structure
    structure_candidates: List[SectionCandidate] = Field(
        default_factory=list,
        description="Downbeat, phrase, and section candidates with confidence (Epic 03.B6)",
    )

    # Epic 03.B7: Diagnostics
    diagnostics: Optional[AnalysisDiagnostics] = Field(
        None,
        description="Analyzer confidence, provenance, and debug stats (Epic 03.B7)",
    )


# ---------------------------------------------------------------------------
# Timestamp query (Epic 03.B2-B3)
# ---------------------------------------------------------------------------


class AnalysisTimestampQuery:
    """
    Epic 03.B2-B3: Query all timing signals at a specific timestamp.

    Given an ``AnalysisIR`` instance, ``at_time(t)`` returns a dict with
    beat_phase, bar_phase, nearest_beat_distance, global_energy, and fft_bands
    ready to inject into a ``RenderContext`` or ``ModulationContext``.
    """

    def __init__(self, analysis: AnalysisIR) -> None:
        self.analysis = analysis

    def _frame_index(self, t: float) -> int:
        """Convert time in seconds to the closest analysis frame index."""
        if self.analysis.fps <= 0:
            return 0
        idx = int(t * self.analysis.fps)
        total = max(1, int(self.analysis.duration * self.analysis.fps))
        return max(0, min(idx, total - 1))

    def at_time(self, t: float) -> Dict[str, Any]:
        """
        Return all timing signals at time ``t`` (seconds).

        Returns:
            Dict with keys: frame_time, beat_phase, bar_phase,
            nearest_beat_distance, global_energy, fft_bands
        """
        i = self._frame_index(t)

        def _get(arr: List[float], default: float = 0.0) -> float:
            return arr[i] if i < len(arr) else default

        fft_bands = [
            env.values[i] if i < len(env.values) else 0.0
            for env in self.analysis.band_envelopes
        ]

        return {
            "frame_time": t,
            "beat_phase": _get(self.analysis.beat_phase),
            "bar_phase": _get(self.analysis.bar_phase),
            "nearest_beat_distance": _get(self.analysis.nearest_beat_distance),
            "global_energy": _get(self.analysis.global_energy),
            "fft_bands": fft_bands,
        }


# ---------------------------------------------------------------------------
# Versioned cache (Epic 03.B1)
# ---------------------------------------------------------------------------


class AnalysisCache:
    """
    Epic 03.B1: In-process versioned analysis cache.

    Cache keys incorporate ``ANALYSIS_SCHEMA_VERSION`` so that any bump to the
    schema constant automatically invalidates all stored entries — no manual
    flushing required.  Entries that were stored under a different schema version
    are rejected on read.
    """

    def __init__(self) -> None:
        self._store: Dict[str, AnalysisIR] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_key(analysis_id: str) -> str:
        """Produce a version-scoped cache key."""
        return f"{ANALYSIS_SCHEMA_VERSION}:{analysis_id}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, analysis_id: str) -> Optional[AnalysisIR]:
        """
        Return the cached analysis, or ``None`` if not found or schema mismatch.

        If the stored entry carries a different ``schema_version`` than the
        current ``ANALYSIS_SCHEMA_VERSION``, it is evicted and ``None`` is
        returned.
        """
        key = self._make_key(analysis_id)
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.schema_version != ANALYSIS_SCHEMA_VERSION:
            del self._store[key]
            return None
        return entry

    def put(self, analysis: AnalysisIR) -> None:
        """Store ``analysis`` in the cache, keyed by its ``analysis_id``."""
        key = self._make_key(analysis.analysis_id)
        self._store[key] = analysis

    def invalidate(self, analysis_id: str) -> None:
        """Remove a single entry from the cache."""
        self._store.pop(self._make_key(analysis_id), None)

    def clear(self) -> None:
        """Evict all entries."""
        self._store.clear()

    def list_ids(self) -> List[str]:
        """Return all currently cached analysis IDs."""
        return [key.split(":", 1)[1] for key in self._store]
