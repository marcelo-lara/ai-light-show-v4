class SeedError(ValueError):
    pass


def validate_seed(seed: object) -> int:
    if seed is None:
        raise SeedError("seed is required and must be an explicit integer")
    if not isinstance(seed, int):
        raise SeedError(f"seed must be int, got {type(seed).__name__}")
    return seed
