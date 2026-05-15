"""
Fixture and POI management

Epic 02: Fixture and POI loading from JSON files
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import json
from pydantic import BaseModel


class CanvasPosition(BaseModel):
    """Position on the 100x50 canvas."""
    x: float
    y: float


class PhysicalPosition(BaseModel):
    """Physical 3D position in the venue."""
    x: float
    y: float
    z: float


class POI(BaseModel):
    """Point of Interest fixture."""
    poi_id: str
    name: str
    canvas_pos: CanvasPosition
    physical_pos: PhysicalPosition
    influence_radius: float = 5.0
    tags: List[str] = []


class FixtureCalibration(BaseModel):
    """Fixture calibration data."""
    target_poi: str
    dmx_pan: int = 127
    dmx_tilt: int = 64


class Fixture(BaseModel):
    """Individual lighting fixture."""
    fixture_id: str
    type: str  # "moving_head", "static_wash", "parcan", etc.
    physical_pos: PhysicalPosition
    calibration: Optional[FixtureCalibration] = None
    canvas_anchor: Optional[CanvasPosition] = None  # For static wash


class FixtureSet(BaseModel):
    """Complete fixture set configuration."""
    schema_version: str
    fixtures: List[Fixture]


class POISet(BaseModel):
    """Complete POI set configuration."""
    schema_version: str
    pois: List[POI]


class FixtureManager:
    """
    Epic 02.F7-F10: Load and manage fixtures and POIs.
    """
    
    def __init__(self, fixtures_dir: str = "data/fixtures"):
        self.fixtures_dir = Path(fixtures_dir)
        self.fixtures: Dict[str, Fixture] = {}
        self.pois: Dict[str, POI] = {}
        self._load_fixtures()
        self._load_pois()
    
    def _load_fixtures(self):
        """Load fixtures from fixtures.json."""
        fixture_file = self.fixtures_dir / "fixtures.json"
        if not fixture_file.exists():
            return
        
        try:
            with open(fixture_file) as f:
                data = json.load(f)
            
            fixture_set = FixtureSet(**data)
            for fixture in fixture_set.fixtures:
                self.fixtures[fixture.fixture_id] = fixture
        except Exception as e:
            print(f"Failed to load fixtures: {e}")
    
    def _load_pois(self):
        """Load POIs from pois.json."""
        poi_file = self.fixtures_dir / "pois.json"
        if not poi_file.exists():
            return
        
        try:
            with open(poi_file) as f:
                data = json.load(f)
            
            poi_set = POISet(**data)
            for poi in poi_set.pois:
                self.pois[poi.poi_id] = poi
        except Exception as e:
            print(f"Failed to load POIs: {e}")
    
    def get_fixtures(self) -> List[Dict[str, Any]]:
        """Get all fixtures as dictionaries."""
        return [f.model_dump() for f in self.fixtures.values()]
    
    def get_pois(self) -> List[Dict[str, Any]]:
        """Get all POIs as dictionaries."""
        return [p.model_dump() for p in self.pois.values()]
    
    def get_fixture(self, fixture_id: str) -> Optional[Fixture]:
        """Get a specific fixture."""
        return self.fixtures.get(fixture_id)
    
    def get_poi(self, poi_id: str) -> Optional[POI]:
        """Get a specific POI."""
        return self.pois.get(poi_id)
