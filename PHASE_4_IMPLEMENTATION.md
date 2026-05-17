# Phase 04 Implementation: Timeline And Direction

**Status:** ✅ COMPLETE  
**Date:** 2026-05-16  
**Version:** 0.4.0

## Overview

Phase 04 implements timeline and scene direction to make shows feel directed across the full song. The engine arranges scenes by musical structure and transitions between them intentionally. Scenes can change on beats, bars, phrases, or sections. Transitions can be hard cuts, crossfades, or beat-flash effects.

## Implementation Summary

### Backend Modules Created

**[backend/app/timeline.py](backend/app/timeline.py) (501 lines)**
- `Scene` model: Complete scene data with timing, preset, automation, and metadata
- `SceneTimeline` model: Timeline container with validation and scene queries
- `AutomationCurve` model: Interpolated curves for intensity and parameter automation
- `TimelineGenerator` class: Auto-generation from sections/phrases/beats with deterministic seeds
- Scene override merging with auto-generated defaults

**[backend/app/transitions.py](backend/app/transitions.py) (413 lines)**
- `Transition` base model: Type, alignment, duration, and parameters
- `HardCutTransition`: Instant scene switch
- `CrossfadeTransition`: Linear blend over duration
- `BeatFlashCutTransition`: White flash then cut on beat onset
- `TransitionAligner` class: Beat/bar/phrase/section alignment
- `TransitionDebugInfo`: Debug metadata with timing and alignment info

### Backend Integration

**[backend/app/models.py](backend/app/models.py)**
- Updated `RenderArtifactMetadata` to schema v1.1 with timeline flags
- `RenderArtifact` now includes optional timeline and transitions fields

**[backend/app/main.py](backend/app/main.py)**
- Updated to v0.4.0
- Added `_timeline_generator` and `_current_timeline` globals
- Added 8 new Phase 04 endpoints:
  - POST `/api/phase04/timeline/generate-from-sections`
  - POST `/api/phase04/timeline/generate-from-phrases`
  - POST `/api/phase04/timeline/generate-from-beats`
  - POST `/api/phase04/timeline/validate`
  - GET `/api/phase04/timeline/current`
  - POST `/api/phase04/timeline/set-current`
  - POST `/api/phase04/transitions/align-to-beat`
  - POST `/api/phase04/transitions/align-to-bar`

### Frontend Types

**[frontend/src/types/phase04.ts](frontend/src/types/phase04.ts) (177 lines)**
- `Scene` interface with timing, musical alignment, automation
- `SceneTimeline` interface with scene collection and metadata
- `Transition` interface with type, alignment, and duration
- `TransitionType` enum: hard_cut, crossfade, beat_flash_cut
- `AlignmentType` enum: beat, bar, phrase, section, frame
- UI state interfaces for timeline and transition editors
- Complete timeline render info structure

### Comprehensive Tests

**[backend/tests/test_phase_04.py](backend/tests/test_phase_04.py) (820 lines)**
- 31 tests covering all Phase 04 functionality
- Scene model tests (creation, alignment, intensity automation)
- Automation curve tests (interpolation types, multiple points)
- Timeline generation tests (sections, phrases, beats)
- Scene override tests
- All transition types (hard cut, crossfade, beat flash cut)
- Transition alignment tests (beat, bar, phrase, section)
- Determinism tests (reproducibility)
- Duration tests (transition timing)
- Multi-scene render tests

### Test Results

```
Phase 04: 31 passed ✅
Phase 03 (backward compat): 26 passed ✅
Docker build: SUCCESS ✅
Application startup: SUCCESS ✅
Health endpoint: OK ✅
Timeline endpoint: FUNCTIONAL ✅
Transition endpoint: FUNCTIONAL ✅
```

### Key Features Implemented

1. **Scene Model (Epic 09.B1)**
   - Timing with musical alignment (beats, bars, phrases, sections)
   - Preset selection with parameter overrides
   - Intensity automation with interpolated curves
   - Per-parameter automation
   - Metadata tagging and tracking (auto-generated vs manual)

2. **Auto-Timeline Generation (Epic 09.B2-B3)**
   - Section-based: One scene per detected section
   - Phrase-based: One scene per phrase
   - Beat-based: Groupable scenes from beat times
   - Deterministic seed generation for reproducibility
   - Preset cycling across scenes

3. **Scene Overrides (Epic 09.B4)**
   - Manual override merging with auto-generated defaults
   - Non-destructive override mechanism
   - Tracking of override source

4. **Transition Types (Epic 10.B2-B4)**
   - Hard cut: Instant switch with zero duration
   - Crossfade: Linear blend over configurable duration
   - Beat flash cut: White flash + fade + hard cut

5. **Beat-Aware Alignment (Epic 10.B5)**
   - Align transitions to beat boundaries
   - Align to bar boundaries (multi-beat grouping)
   - Align to phrase/section boundaries

6. **Determinism & Reproducibility**
   - Same seed + section → identical timeline
   - Same transition params → identical output
   - Frame-aware seeding for variation

7. **Artifact Integration (Epic 09.B7, 10.B6)**
   - Timeline metadata in render artifacts
   - Transition metadata in render artifacts
   - Schema versioning for compatibility

---

## Epic 09: Timeline Director

### Backend Track

#### 09.B1 🚀 Scene model
**File:** `backend/app/timeline.py`

Scene data structure:
- `start_time`: Start time in seconds
- `start_beat`: Optional beat alignment
- `start_bar`: Optional bar alignment
- `start_phrase`: Optional phrase alignment
- `start_section`: Optional section alignment
- `end_time`: End time in seconds
- `preset_id`: ID of the preset to use
- `seed`: Random seed for deterministic rendering
- `params`: Dict[str, Any] for preset parameter overrides
- `intensity`: Float 0.0-1.0 for overall intensity
- `intensity_automation`: Optional automation curve
- `param_automation`: Dict[str, automation curve] for per-parameter automation
- `metadata`: Optional tags, notes, author

#### 09.B2 🚀 Auto timeline from sections
**File:** `backend/app/timeline.py`

Auto-generate first-pass timeline from detected sections:
- `auto_timeline_from_sections()`: Takes song IR and generates a Scene per section
- Cycles through available presets or uses a default
- Seeds vary by section for determinism
- Aligned to section boundaries

#### 09.B3 🚀 Auto timeline from phrases or beats
**File:** `backend/app/timeline.py`

Fallback auto-generation:
- `auto_timeline_from_phrases()`: Generate scenes from phrase grouping
- `auto_timeline_from_beats()`: Fine-grained scene generation per N beats
- Used when section detection fails or for detailed control

#### 09.B4 🚀 Scene overrides
**File:** `backend/app/timeline.py`

Support manual scene edits:
- `SceneTimeline`: Holds auto-generated + manual overrides
- Merging strategy: manual overrides shadow auto-generated defaults
- No breaking of auto-generated timeline on override

#### 09.B5 🚀 Scene-level intensity automation
**File:** `backend/app/timeline.py`

Automation curves:
- `AutomationCurve`: Type, control points (time/value), interpolation
- Intensity automation applies to all layers
- Control points: (timestamp, value) pairs

#### 09.B6 🚀 Scene-level parameter automation
**File:** `backend/app/timeline.py`

Per-parameter automation:
- `param_automation`: Dict[param_name -> AutomationCurve]
- Applied per-frame during render
- Interpolates between control points

#### 09.B7 🚀 Artifact integration
**File:** `backend/app/models.py`

Include timeline metadata in render artifacts:
- `RenderArtifact.timeline`: Optional SceneTimeline
- Scene information persisted for analysis

### Frontend Track

#### 09.F1 🚀 Timeline types
**File:** `frontend/src/types/phase04.ts`

Frontend types:
- `Scene`: Scene data structure
- `SceneTimeline`: Timeline collection
- `AutomationCurve`: Automation structure
- `TimelineMetadata`: Metadata for UI

#### 09.F2 🚀 Timeline display readiness
**File:** `frontend/src/types/phase04.ts`

UI-facing shape ready for future timeline editor:
- `TimelineUIState`: For timeline view
- Serialization-ready types

### Validation Track

#### 09.V1 🚀 Multi-scene render test
**File:** `backend/tests/test_phase_04.py`

Tests prove multi-scene rendering:
- `test_multi_scene_timeline_generation`: Generate timeline with 3+ scenes
- `test_timeline_with_different_presets_per_scene`: Each scene uses different preset

#### 09.V2 🚀 Alignment test
**File:** `backend/tests/test_phase_04.py`

Tests prove scene alignment:
- `test_scenes_align_to_section_boundaries`: Auto scenes at section points
- `test_scenes_can_align_to_beats`: Beat alignment works

#### 09.V3 🚀 Override test
**File:** `backend/tests/test_phase_04.py`

Tests prove manual overrides persist:
- `test_scene_override_shadows_auto_generated`: Override doesn't break auto

---

## Epic 10: Transition System

### Backend Track

#### 10.B1 🚀 Transition model
**File:** `backend/app/transitions.py`

Transition data structure:
- `type`: TransitionType enum (hard_cut, crossfade, beat_flash_cut)
- `alignment`: Alignment enum (beat, bar, phrase, section, frame)
- `duration`: Duration in seconds
- `params`: Dict[str, Any] for transition-specific params
- `metadata`: Tags, notes

#### 10.B2 🚀 Hard cut
**File:** `backend/app/transitions.py`

Hard cut transition:
- `HardCutTransition`: Instant scene switch
- Params: (none)
- No intermediate frames

#### 10.B3 🚀 Crossfade
**File:** `backend/app/transitions.py`

Crossfade transition:
- `CrossfadeTransition`: Linear fade from old to new
- Params: duration (1-3 seconds typical)
- Interpolates preset parameters and renders both

#### 10.B4 🚀 Beat flash cut
**File:** `backend/app/transitions.py`

Beat-reactive transition:
- `BeatFlashCutTransition`: Full white flash then hard cut
- Params: flash_duration, decay
- Syncs to beat onset

#### 10.B5 🚀 Beat-aware alignment
**File:** `backend/app/transitions.py`

Scene transitions align to musical points:
- Beat, bar, phrase, or section boundaries
- `align_transition_to_beat()`: Snap to nearest beat
- `align_transition_to_bar()`: Snap to nearest bar

#### 10.B6 🚀 Transition metadata
**File:** `backend/app/models.py`

Include transitions in render artifacts:
- `RenderArtifact.transitions`: List[Transition]
- Transition metadata persisted

#### 10.B7 🚀 Transition debug info
**File:** `backend/app/transitions.py`

Expose debug information:
- Transition timing info
- Alignment decisions
- Parameter values during transition

### Frontend Track

#### 10.F1 🚀 Transition types
**File:** `frontend/src/types/phase04.ts`

Frontend types:
- `Transition`: Transition data
- `TransitionType`: Type enum
- `TransitionMetadata`: UI metadata

#### 10.F2 🚀 Transition preview readiness
**File:** `frontend/src/types/phase04.ts`

UI-facing shape ready for transition preview:
- `TransitionUIState`: For preview view
- Type-safe metadata

### Validation Track

#### 10.V1 🚀 Deterministic transition test
**File:** `backend/tests/test_phase_04.py`

Tests prove reproducibility:
- `test_crossfade_determinism`: Same seed → identical transition
- `test_beat_flash_determinism`: Reproducible beat flash

#### 10.V2 🚀 Duration test
**File:** `backend/tests/test_phase_04.py`

Tests prove duration consistency:
- `test_transition_duration_honored`: Transition applies over correct timespan
- `test_hard_cut_zero_duration`: Hard cut is instant

#### 10.V3 🚀 Alignment test
**File:** `backend/tests/test_phase_04.py`

Tests prove alignment:
- `test_transition_aligns_to_beat`: Transition snaps to beat
- `test_transition_aligns_to_bar`: Transition snaps to bar

---

## Technical Notes

### Timeline and Scene Structure

Scenes are time-slices within a song where a particular preset/look is active. Each scene:
1. Occupies a specific time window [start_time, end_time]
2. Can be aligned to musical boundaries (beats, bars, phrases, sections)
3. Uses a preset with optional parameter overrides
4. Can have intensity and parameter automation curves
5. Has a deterministic seed for reproducibility

### Auto-Generation Strategy

The timeline auto-generation follows this priority:
1. **Section-based** (default): One scene per detected section
2. **Phrase-based** (fallback): One scene per detected phrase
3. **Beat-based** (emergency): One scene per N beats

### Transition Mechanics

Transitions occur between scenes and can be:
1. **Hard cuts**: Instant switch (0 duration)
2. **Crossfades**: Linear blend over N seconds
3. **Beat flashes**: White flash on beat onset, then cut

All transitions are beat-aware and can snap to musical boundaries.

### Determinism

- Scene seeds are deterministic based on song + section + auto-gen parameters
- Transition output is reproducible given seed and render time
- Same render request → identical frame output

---

## Implementation Status

- [x] 09.B1-B7: Scene and timeline models
- [x] 10.B1-B7: Transition models and implementations
- [x] Frontend types (09.F1-F2, 10.F1-F2)
- [x] Integration with render artifacts
- [x] Validation tests (09.V1-V3, 10.V1-V3)
- [x] Main.py integration
- [x] Docker build and smoke test

**Test Results:** ✅ All 31 Phase 04 tests PASSED  
**Backward Compatibility:** ✅ All 26 Phase 03 tests PASSED  
**Application Health:** ✅ Backend starts successfully, all endpoints functional

