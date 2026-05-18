from __future__ import annotations

import math


def apply_op(value: float, op: dict, state: dict) -> float:
    name = op.get("op", "")
    if name == "scale":
        lo = float(op.get("min", 0.0))
        hi = float(op.get("max", 1.0))
        return value * (hi - lo) + lo
    if name == "clamp":
        lo = float(op.get("min", 0.0))
        hi = float(op.get("max", 1.0))
        return max(lo, min(hi, value))
    if name == "invert":
        return 1.0 - value
    if name == "curve":
        power = float(op.get("power", 1.0))
        return math.pow(max(value, 0.0), power)
    if name in ("smooth", "lag"):
        alpha = float(op.get("alpha", 0.1))
        key = op.get("key", "_default")
        prev = float(state.get(key, value))
        result = prev + alpha * (value - prev)
        state[key] = result
        return result
    if name == "quantize":
        steps = int(op.get("steps", 8))
        if steps < 1:
            return value
        return round(value * steps) / steps
    return value


def apply_ops(value: float, ops: list[dict], state: dict) -> float:
    for op in ops:
        value = apply_op(value, op, state)
    return value
