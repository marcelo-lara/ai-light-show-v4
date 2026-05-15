"""
Render Contract Implementation

Epic 01.B2: Stable render_id generation from reproducible inputs.
Epic 01.B3: Explicit seed handling.
Epic 01.B4: Backend compatibility checks.
"""

import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime


def generate_render_id(
    song_id: str,
    preset_id: str,
    seed: int,
    params: Dict[str, Any]
) -> str:
    """
    Epic 01.B2: Generate a stable render_id from reproducible inputs.
    
    Creates a deterministic hash from song_id, preset_id, seed, and params.
    The same inputs always produce the same render_id.
    
    Args:
        song_id: The source song ID
        preset_id: The preset used
        seed: The random seed for rendering
        params: The render parameters
        
    Returns:
        A stable render_id string
    """
    input_data = {
        "song_id": song_id,
        "preset_id": preset_id,
        "seed": seed,
        "params": json.dumps(params, sort_keys=True, default=str)
    }
    
    input_str = json.dumps(input_data, sort_keys=True)
    hash_digest = hashlib.sha256(input_str.encode()).hexdigest()
    
    return f"render_{hash_digest[:16]}"


def validate_artifact_compatibility(artifact_dict: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Epic 01.B4: Backend compatibility checks.
    
    Validates that a render artifact has all required fields and compatible schema version.
    
    Args:
        artifact_dict: The artifact dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = [
        "schema_version",
        "render_id",
        "preset_id",
        "preset_version",
        "seed",
        "song_id",
        "analysis_id",
        "fps",
        "duration",
        "frame_count"
    ]
    
    # Check for missing fields
    for field in required_fields:
        if field not in artifact_dict:
            return False, f"Missing required field: {field}"
    
    # Check schema version compatibility
    schema_version = artifact_dict.get("schema_version", "")
    if not schema_version.startswith("1."):
        return False, f"Unsupported schema version: {schema_version}. Expected 1.x"
    
    return True, None


def validate_seed(seed: Optional[int]) -> tuple[bool, Optional[str]]:
    """
    Epic 01.B3: Explicit seed validation.
    
    Ensures seed is present and valid for deterministic rendering.
    
    Args:
        seed: The seed value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if seed is None:
        return False, "Seed is required for deterministic rendering"
    
    if not isinstance(seed, int):
        return False, f"Seed must be an integer, got {type(seed).__name__}"
    
    if seed < 0:
        return False, "Seed must be non-negative"
    
    return True, None


class RenderIdGenerator:
    """
    Service for managing render IDs and their stability across renders.
    """
    
    def __init__(self):
        self._cache: Dict[str, str] = {}
    
    def get_or_generate_render_id(
        self,
        song_id: str,
        preset_id: str,
        seed: int,
        params: Dict[str, Any]
    ) -> str:
        """
        Get cached render_id or generate a new one.
        
        Args:
            song_id: The source song ID
            preset_id: The preset used
            seed: The random seed
            params: The render parameters
            
        Returns:
            Stable render_id
        """
        cache_key = f"{song_id}:{preset_id}:{seed}"
        
        if cache_key not in self._cache:
            self._cache[cache_key] = generate_render_id(song_id, preset_id, seed, params)
        
        return self._cache[cache_key]
