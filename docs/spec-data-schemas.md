# Specification: Data Schemas & File Structure

## Directory Structure
To maintain a clean separation of concerns:

1. **`data/fixtures/` (Read-Only Configs)**
   Source of truth for the physical room layout, POIs, and fixture addressing. The engine reads these to understand the environment.
2. **`data/artifacts/` (Engine Outputs)**
   Source of truth for generated IR caches, binary canvases, and DMX export manifests. The engine writes these here.

---

## 1. Fixture & POI Configs (`data/fixtures/`)

### `pois.json`
Defines the Points of Interest in the room. They act as calibration points, targets, and shader anchors.

```json
{
  "schema_version": "1.0",
  "pois": [
    {
      "poi_id": "ref_0_0_0",
      "name": "Room Center Origin",
      "canvas_pos": {"x": 50, "y": 25},
      "physical_pos": {"x": 0.0, "y": 0.0, "z": 0.0},
      "influence_radius": 5.0,
      "tags": ["calibration", "origin"]
    },
    {
      "poi_id": "poi_dj_booth",
      "name": "DJ Booth",
      "canvas_pos": {"x": 50, "y": 40},
      "physical_pos": {"x": 0.0, "y": 1.5, "z": -2.0},
      "influence_radius": 10.0,
      "tags": ["target", "collision"]
    }
  ]
}
```

### `fixtures.json`
Defines the actual lighting hardware, its DMX address, and its calibration data targeting specific POIs.

```json
{
  "schema_version": "1.0",
  "fixtures": [
    {
      "fixture_id": "mh_left_1",
      "type": "moving_head",
      "physical_pos": {"x": -4.0, "y": 3.0, "z": 0.0},
      "calibration": {
        "target_poi": "ref_0_0_0",
        "dmx_pan": 127,
        "dmx_tilt": 64
      }
    },
    {
      "fixture_id": "parcan_back_1",
      "type": "static_wash",
      "canvas_anchor": {"x": 10, "y": 10},
      "calibration": null
    }
  ]
}
```

---

## 2. Artifacts (`data/artifacts/`)
When a show is analyzed and rendered, the outputs are stored here.

- **`{song_id}.analysis.json`**: The Essentia-extracted Intermediate Representation (IR).
- **`{song_id}.{canvas_name}.meta.json`**: The Render Contract metadata (seed, parameters, schema).
- **`{song_id}.{canvas_name}.chunks/`**: The chunked binary payload representing the `100x50` visual math over time (Step 2.4).
- **`{song_id}.{canvas_name}.dmx.json`**: The final Step 3 mapped DMX instructions (Pan/Tilt/Color/Dimmer) over time.