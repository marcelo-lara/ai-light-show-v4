# Specification: Moving Head Math & Translation

## Objective
Translate a 2D canvas target coordinate `[Cx, Cy]` into physical DMX Pan and Tilt values for a moving head, using a known Point of Interest (POI) calibration reference.

## The Calibration Reference (`ref_0_0_0`)
To avoid requiring perfect tape-measured 3D models of every room, we use a reference POI. 
- **`ref_0_0_0`**: Represents the physical origin `[x: 0, y: 0, z: 0]`.
- A moving head will have a stored DMX Pan/Tilt calibration value that perfectly points its beam at `ref_0_0_0`.
- The 2D math canvas (100x50) is mapped to a physical plane in the room (e.g., the back wall or the floor).

## The Translation Pipeline

### Step 1: Canvas (2D) to Physical Space (3D)
Every pixel on the `100x50` canvas maps to a physical `[X, Y, Z]` coordinate relative to `ref_0_0_0`.
- If `ref_0_0_0` is the center of the canvas `[50, 25]`, then a target pixel at `[75, 25]` represents a physical offset (e.g., +2 meters in X, 0 in Y, 0 in Z).
- **Target 3D Coordinate (`T`)**: `[Tx, Ty, Tz]`

### Step 2: Vector Calculation
The Moving Head has a known physical installation position: **`H`** `[Hx, Hy, Hz]`.
We calculate the 3D directional vector **`V`** from the Moving Head to the Target:
```text
Vx = Tx - Hx
Vy = Ty - Hy
Vz = Tz - Hz
```

### Step 3: Trigonometric Mapping to Pan/Tilt
Using the vector `V`, we calculate the absolute angles required to point the moving head at the target.

**Pan Angle (θ):** 
The rotation around the Y-axis (vertical axis).
```text
Pan (θ) = atan2(Vx, Vz)
```

**Tilt Angle (φ):**
The rotation around the X/Z plane (horizontal elevation).
```text
Horizontal_Distance = sqrt(Vx^2 + Vz^2)
Tilt (φ) = atan2(Vy, Horizontal_Distance)
```

### Step 4: DMX Value Interpolation
Absolute angles (in radians/degrees) must be converted to DMX values (0-255 for 8-bit, or 0-65535 for 16-bit).
We use the calibration point `ref_0_0_0` to lock the offset:
1. Calculate the theoretical Pan/Tilt angles for `ref_0_0_0`.
2. Compare them against the *actual* calibrated DMX values stored for `ref_0_0_0`.
3. Calculate the Delta.
4. Apply the Delta to the newly calculated target Pan/Tilt angles.
5. Clamp the final values to the DMX limits of the fixture.