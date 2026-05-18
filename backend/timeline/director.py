from __future__ import annotations

import math

from analysis.schema import AnalysisIRV1
from .schema import Scene, TimelineV1

_DEFAULT_PRESET = "undersea_pulse_01"
_FALLBACK_SCENE_DURATION = 8.0


def build_from_sections(ir: AnalysisIRV1, song_id: str) -> TimelineV1:
    sections = ir.sections
    if sections:
        scenes = [
            Scene(
                scene_id=f"section_{i}",
                start=s.start,
                end=s.end,
                preset_id=_DEFAULT_PRESET,
                seed=i,
            )
            for i, s in enumerate(sections)
        ]
        return TimelineV1(song_id=song_id, source="auto_sections", scenes=scenes)

    return _from_beats(ir, song_id)


def _from_beats(ir: AnalysisIRV1, song_id: str) -> TimelineV1:
    if not ir.beats:
        duration = _DEFAULT_SCENE_DURATION
        return TimelineV1(
            song_id=song_id,
            source="auto_beats",
            scenes=[Scene(scene_id="s0", start=0.0, end=duration, preset_id=_DEFAULT_PRESET)],
        )

    # group beats into ~8-bar scenes (assume 4/4 → 32 beats per scene)
    beats = [b.time for b in ir.beats]
    beats_per_scene = 32
    scenes: list[Scene] = []
    for i in range(0, len(beats), beats_per_scene):
        chunk = beats[i:i + beats_per_scene]
        start = chunk[0]
        end = chunk[-1]
        if i + beats_per_scene < len(beats):
            end = beats[i + beats_per_scene]
        scenes.append(
            Scene(
                scene_id=f"phrase_{i // beats_per_scene}",
                start=start,
                end=end,
                preset_id=_DEFAULT_PRESET,
                seed=i // beats_per_scene,
            )
        )
    return TimelineV1(song_id=song_id, source="auto_beats", scenes=scenes)


_DEFAULT_SCENE_DURATION = _FALLBACK_SCENE_DURATION
