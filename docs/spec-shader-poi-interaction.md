# Specification: Shader & POI Interactions

## Objective
Define how Math Canvas layers (shaders) utilize Points of Interest (POIs) to create dynamic, spatially-aware effects on the `100x50` grid.

## Core Concepts
POIs in the engine are more than just rendering targets; they act as "event nodes" or "gravity wells" on the 2D canvas.

### 1. Start (Spawning)
A shader can use a POI as an origin point.
- **Example:** The `raindrops` shader or `spectroid_chase`.
- **Mechanism:** On a detected beat or musical onset, the engine queries `pois.json` for active anchor POIs. The shader sets its initial origin `[x, y]` to the canvas coordinates of the POI. The wave/particle expands outward from that exact pixel.

### 2. End (Collision / Termination)
A shader can use a POI as a termination or collision point.
- **Example:** A sweeping wave hits a specific POI (like a DJ booth or drum kit) and explodes into a particle burst, or simply dies.
- **Mechanism:** The engine checks the distance between the moving shader construct (e.g., the leading edge of a wave) and the POI's `[x, y]`. If `distance < collision_radius`, the layer triggers an `on_poi_hit` event, altering the pixel data (e.g., rendering a bright flash) and stopping further calculation for that construct.

### 3. Pass-Thru (Speed & Gravity Modulation)
A shader can interact continuously with a POI as it travels near it, slowing down, speeding up, or bending.
- **Example:** A "black hole" effect where a scanning line slows down as it crosses the center POI, building tension, before snapping rapidly across the rest of the canvas.
- **Mechanism:** 
  At each frame `t`, calculate the distance `d` from the moving pixel/particle to the POI.
  ```python
  d = distance(particle.pos, poi.pos)
  if d < poi.influence_radius:
      # Slow down as it gets closer (tension building)
      speed_multiplier = clamp((d / poi.influence_radius), 0.1, 1.0)
      particle.velocity *= speed_multiplier
  ```

## Implementation Rule
When authoring layers (Epic 04 / Epic 11 / Epic 12), layers should accept a `poi_list` parameter. 
Backend shader implementations should live in `backend/shaders/`, and the `render_frame()` loop for the layer will iterate over these POIs to apply the Start, End, or Pass-Thru mathematics before finalizing the RGB values for the 100x50 grid.