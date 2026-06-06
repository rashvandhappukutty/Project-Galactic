# backend/models/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Any

class StarSchema(BaseModel):
    id: Optional[str] = None
    star_id: Optional[str] = None
    name: str
    star_type: str
    mass: float
    temperature: float
    luminosity: float
    x: float
    y: float
    z: float
    region: Optional[str] = None

class PlanetSchema(BaseModel):
    planet_id: str
    planet_name: str
    star_id: str
    planet_type: str
    orbital_distance_au: float
    mass: float
    radius: float
    gravity: float
    temperature: float
    water_percentage: float
    atmosphere_type: str
    resource_score: float
    habitability_score: float

class SpeciesSchema(BaseModel):
    species_id: str
    species_name: str
    homeworld: str
    diet: str
    lifespan: float
    kardashev_level: float

class EmpireSchema(BaseModel):
    empire_id: str
    empire_name: str
    capital_world: str
    population: float
    gdp: float
    power_index: float
    colonies_count: int

class UnifiedSearchResponse(BaseModel):
    stars: List[Any]
    planets: List[Any]
    empires: List[Any]
    figures: List[Any]
    events: List[Any]
    stories: List[Any]
    news: List[Any]
