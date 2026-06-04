"""Quick smoke test for Phase 2 planet modules."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from dataclasses import dataclass
from simulation.planets.planet import Planet, PlanetType, AtmosphereType
from simulation.planets.planet_generator import PlanetGenerator
from simulation.planets.habitability import HabitabilityEngine

@dataclass
class MockSystem:
    star_id: str = "abc123"
    star_name: str = "GDE-4221"
    star_luminosity: float = 1.0
    star_temperature: float = 5778.0
    hz_inner: float = 0.95
    hz_outer: float = 1.37
    planet_count: int = 6

print("=" * 70)
print("  PHASE 2 SMOKE TEST - Planet Generation & Habitability")
print("=" * 70)

# 1. Generate planets
mock = MockSystem()
gen = PlanetGenerator(seed=42)
planets = gen.generate_planets(mock)
print(f"\nGenerated {len(planets)} planets for {mock.star_name}:\n")
for p in planets:
    print(f"  {p}")

# 2. Score habitability & resources
engine = HabitabilityEngine(seed=42)
systems_dict = {mock.star_id: mock}
engine.process_all_planets(planets, systems_dict)

print(f"\nAfter habitability & resource scoring:\n")
for p in planets:
    cls = engine.classify_habitability(p.habitability_score)
    print(f"  {p}  ->  {cls}")

# 3. Test serialization round-trip
d = planets[0].to_dict()
p2 = Planet.from_dict(d)
assert p2.planet_name == planets[0].planet_name
assert p2.planet_type == planets[0].planet_type
print("\n[OK] Serialisation round-trip passed.")

# 4. Batch generation
systems = [MockSystem(star_id=f"s{i}", star_name=f"Star-{i}", planet_count=i+1) for i in range(5)]
all_planets = gen.generate_all_planets(systems)
print(f"[OK] Batch generation: {len(all_planets)} planets across {len(systems)} systems.")

print("\n" + "=" * 70)
print("  ALL TESTS PASSED")
print("=" * 70)
