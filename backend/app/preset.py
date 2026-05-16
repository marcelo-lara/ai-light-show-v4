"""
Preset Schema and Registry

Epic 06: Preset Schema
Defines the preset format, parameter schema, layer stacks, palettes, and blend modes.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List, Union, Literal
from pydantic import BaseModel, Field, field_validator


class ParameterType(str, Enum):
    """Supported parameter types in preset schema."""
    FLOAT = "float"
    INT = "int"
    BOOLEAN = "boolean"
    STRING = "string"
    COLOR = "color"
    CHOICE = "choice"


class BlendMode(str, Enum):
    """Supported blend modes for layers."""
    MAX = "max"
    ADD = "add"
    ALPHA = "alpha"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    DIFFERENCE = "difference"
    MASK = "mask"
    REPLACE = "replace"


class ParameterConstraint(BaseModel):
    """
    Epic 06.B2: Parameter constraints and bounds.
    
    Defines validation rules for a parameter.
    """
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    step_size: Optional[Union[int, float]] = None
    choices: Optional[List[str]] = None  # For CHOICE type


class ParameterSchema(BaseModel):
    """
    Epic 06.B2: Typed parameter with metadata.
    
    Defines a single preset parameter with type, default, bounds, UI grouping.
    """
    name: str = Field(..., description="Parameter identifier (snake_case)")
    type: ParameterType = Field(..., description="Parameter type")
    label: str = Field(..., description="Human-readable label for UI")
    description: str = Field(default="", description="Parameter description")
    default_value: Any = Field(..., description="Default value for this parameter")
    constraint: Optional[ParameterConstraint] = None
    ui_group: str = Field(default="General", description="UI group for organization")
    
    @field_validator("default_value")
    @classmethod
    def validate_default_matches_type(cls, v, info):
        """Ensure default value matches declared type."""
        if info.data.get("type") == ParameterType.INT:
            assert isinstance(v, int), f"INT parameter default must be int, got {type(v)}"
        elif info.data.get("type") == ParameterType.FLOAT:
            assert isinstance(v, (int, float)), f"FLOAT parameter default must be number"
        elif info.data.get("type") == ParameterType.BOOLEAN:
            assert isinstance(v, bool), f"BOOLEAN parameter default must be bool"
        elif info.data.get("type") == ParameterType.STRING:
            assert isinstance(v, str), f"STRING parameter default must be string"
        return v


class ColorPalette(BaseModel):
    """
    Epic 06.B4: Color palette definition.
    
    Defines a set of named colors for use in preset rendering.
    """
    name: str = Field(..., description="Palette identifier")
    colors: Dict[str, str] = Field(..., description="Named colors as hex values (#RRGGBB)")
    description: Optional[str] = None


class LayerReference(BaseModel):
    """
    Epic 06.B3: Reference to a layer in the layer registry.
    
    Defines a layer instance with per-layer parameters.
    """
    layer_id: str = Field(..., description="ID of the layer in the registry")
    label: str = Field(..., description="Display label for this layer instance")
    order: int = Field(..., description="Z-order (0=bottom, higher=on top)")
    blend_mode: BlendMode = Field(default=BlendMode.ALPHA, description="Blend mode for this layer")
    enabled: bool = Field(default=True, description="Whether layer is active")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0, description="Layer opacity")
    params: Dict[str, Any] = Field(default_factory=dict, description="Layer-specific parameters")


class PresetMetadata(BaseModel):
    """
    Epic 06.B1: Preset identity and metadata.
    
    Defines preset name, version, display fields, tags, and description.
    """
    preset_id: str = Field(..., description="Unique preset identifier (snake_case)")
    version: str = Field("1.0", description="Semantic version (major.minor)")
    label: str = Field(..., description="Human-readable name")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    description: str = Field(default="", description="Detailed preset description")
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)


class PresetDefinition(BaseModel):
    """
    Epic 06.B1-B5: Complete preset schema.
    
    Defines a complete preset with metadata, parameters, layer stack, palette, and blend modes.
    """
    metadata: PresetMetadata
    
    # Epic 06.B2: Parameter schema
    parameters: Dict[str, ParameterSchema] = Field(
        default_factory=dict,
        description="Preset-level parameters accessible to all layers"
    )
    
    # Epic 06.B4: Palette
    palette: Optional[ColorPalette] = None
    
    # Epic 06.B3: Layer stack
    layers: List[LayerReference] = Field(
        ...,
        description="Ordered list of layers (bottom to top)"
    )
    
    # Epic 06.B5: Blend modes
    default_blend_mode: BlendMode = Field(default=BlendMode.ALPHA)
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "preset_id": "undersea_waves",
                    "version": "1.0",
                    "label": "Undersea Waves",
                    "tags": ["wave", "water", "parcan"],
                    "description": "Three layered sine waves moving left to right"
                },
                "parameters": {
                    "base_color": {
                        "name": "base_color",
                        "type": "color",
                        "label": "Base Color",
                        "default_value": "#0000FF"
                    },
                    "wave_speed": {
                        "name": "wave_speed",
                        "type": "float",
                        "label": "Wave Speed",
                        "default_value": 1.0,
                        "constraint": {"min_value": 0.1, "max_value": 5.0}
                    }
                },
                "palette": {
                    "name": "ocean",
                    "colors": {
                        "deep": "#001a4d",
                        "mid": "#0033cc",
                        "light": "#0066ff"
                    }
                },
                "layers": [
                    {
                        "layer_id": "wave",
                        "label": "Wave Layer 1",
                        "order": 0,
                        "blend_mode": "add"
                    }
                ]
            }
        }


class PresetValidationError(Exception):
    """Raised when preset validation fails."""
    pass


class PresetValidator:
    """
    Epic 06.B6: Preset validation.
    
    Validates presets before render time with actionable errors.
    """
    
    @staticmethod
    def validate_preset(preset: PresetDefinition, layer_registry: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Validate a preset definition.
        
        Args:
            preset: PresetDefinition to validate
            layer_registry: Optional registry of available layers
        
        Returns:
            List of validation errors (empty if valid)
        
        Raises:
            PresetValidationError: If validation fails with critical errors
        """
        errors = []
        
        # Validate metadata
        if not preset.metadata.preset_id:
            errors.append("Preset ID cannot be empty")
        if not preset.metadata.label:
            errors.append("Preset label cannot be empty")
        
        # Validate parameters
        for param_name, param_schema in preset.parameters.items():
            if param_schema.name != param_name:
                errors.append(f"Parameter name mismatch: key '{param_name}' vs schema '{param_schema.name}'")
            
            # Validate constraints
            if param_schema.constraint:
                constraint = param_schema.constraint
                default = param_schema.default_value
                
                if constraint.min_value is not None and default < constraint.min_value:
                    errors.append(
                        f"Parameter '{param_name}' default {default} below minimum {constraint.min_value}"
                    )
                if constraint.max_value is not None and default > constraint.max_value:
                    errors.append(
                        f"Parameter '{param_name}' default {default} above maximum {constraint.max_value}"
                    )
                if param_schema.type == ParameterType.CHOICE and constraint.choices:
                    if default not in constraint.choices:
                        errors.append(
                            f"Parameter '{param_name}' default '{default}' not in choices {constraint.choices}"
                        )
        
        # Validate layers
        if not preset.layers:
            errors.append("Preset must contain at least one layer")
        
        layer_ids_seen = set()
        for idx, layer in enumerate(preset.layers):
            # Check for duplicate layer references
            layer_key = f"{layer.layer_id}:{idx}"
            if layer_key in layer_ids_seen:
                errors.append(f"Duplicate layer instance at index {idx}")
            layer_ids_seen.add(layer_key)
            
            # Validate layer registry if provided
            if layer_registry and layer.layer_id not in layer_registry:
                errors.append(f"Layer '{layer.layer_id}' not found in registry")
            
            # Validate layer parameters
            if not layer.label:
                errors.append(f"Layer {idx} must have a label")
            
            if layer.opacity < 0.0 or layer.opacity > 1.0:
                errors.append(f"Layer {idx} opacity must be between 0.0 and 1.0, got {layer.opacity}")
        
        # Check z-order uniqueness
        z_orders = [layer.order for layer in preset.layers]
        if len(z_orders) != len(set(z_orders)):
            errors.append("Layer z-orders must be unique")
        
        # Validate palette colors
        if preset.palette:
            for color_name, color_value in preset.palette.colors.items():
                if not color_value.startswith("#") or len(color_value) != 7:
                    errors.append(f"Palette color '{color_name}' invalid hex format: {color_value}")
        
        if errors:
            error_message = "Preset validation failed:\n  " + "\n  ".join(errors)
            raise PresetValidationError(error_message)
        
        return errors


class PresetRegistry:
    """
    Epic 06: Preset registry for loading and managing presets.
    """
    
    def __init__(self):
        self.presets: Dict[str, PresetDefinition] = {}
        self.layer_registry: Optional[Dict[str, Any]] = None
    
    def register_preset(self, preset: PresetDefinition, validate: bool = True) -> None:
        """
        Register a preset in the registry.
        
        Args:
            preset: PresetDefinition to register
            validate: Whether to validate before registering
        
        Raises:
            PresetValidationError: If validation enabled and preset invalid
        """
        if validate:
            PresetValidator.validate_preset(preset, self.layer_registry)
        
        preset_key = f"{preset.metadata.preset_id}:{preset.metadata.version}"
        self.presets[preset_key] = preset
    
    def get_preset(self, preset_id: str, version: str = "latest") -> Optional[PresetDefinition]:
        """Get a preset by ID and version."""
        if version == "latest":
            # Get the highest version
            matching = [p for p in self.presets if p.startswith(f"{preset_id}:")]
            if not matching:
                return None
            return self.presets[max(matching)]
        return self.presets.get(f"{preset_id}:{version}")
    
    def list_presets(self) -> List[PresetDefinition]:
        """List all registered presets."""
        return list(self.presets.values())
