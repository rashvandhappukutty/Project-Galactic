# backend/main.py
import os
import glob
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from database import init_database, get_db_connection
from config import DATASETS_DIR

# Import modular API routers
from api.stars import router as stars_router
from api.planets import router as planets_router
from api.species import router as species_router
from api.civilizations import router as civilizations_router
from api.empires import router as empires_router
from api.economy import router as economy_router
from api.ftl import router as ftl_router
from api.wars import router as wars_router
from api.history import router as history_router
from api.stories import router as stories_router
from api.search import router as search_router
from api.analytics import router as analytics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler that initializes the SQLite database during startup."""
    init_database()
    yield

app = FastAPI(
    title="The Galactic Dream Engine - Digital Twin API",
    description="Unified API interface for stars, planetary orbits, historical chronicles, and economy.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
def health_check():
    """Returns the service health status, including database connection and dataset logs."""
    dataset_count = 0
    if os.path.exists(DATASETS_DIR):
        dataset_count = len(glob.glob(os.path.join(DATASETS_DIR, "*.csv")))
        
    db_connected = False
    table_counts = {}
    try:
        conn = get_db_connection()
        db_connected = True
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        for t in tables:
            t_name = t['name']
            count = conn.execute(f"SELECT COUNT(*) FROM [{t_name}]").fetchone()[0]
            table_counts[t_name] = count
        conn.close()
    except Exception as e:
        print(f"Health check SQLite error: {e}")
        
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database_connected": db_connected,
        "dataset_count": dataset_count,
        "loaded_tables_count": len(table_counts),
        "tables": table_counts
    }

@app.get("/api/dashboard")
def get_dashboard_summary():
    """Returns aggregated summary metrics of the simulation."""
    conn = get_db_connection()
    try:
        total_stars = conn.execute("SELECT COUNT(*) FROM stars").fetchone()[0]
        total_planets = conn.execute("SELECT COUNT(*) FROM planets").fetchone()[0]
        
        # Habitability check fallback
        try:
            total_life_worlds = conn.execute("SELECT COUNT(*) FROM life_catalog WHERE life_stage > 0").fetchone()[0]
        except Exception:
            total_life_worlds = 100
            
        total_species = conn.execute("SELECT COUNT(*) FROM species_catalog").fetchone()[0]
        total_civilizations = conn.execute("SELECT COUNT(*) FROM civilizations").fetchone()[0]
        total_empires = conn.execute("SELECT COUNT(*) FROM empires").fetchone()[0]
        
        # Wars count fallback
        try:
            total_wars = conn.execute("SELECT COUNT(*) FROM wars").fetchone()[0]
        except Exception:
            total_wars = 0
            
        total_events = conn.execute("SELECT COUNT(*) FROM galactic_history_master").fetchone()[0]
        max_year = conn.execute("SELECT MAX(year) FROM galactic_history_master").fetchone()[0] or 1000000
        
        return {
            "total_stars": total_stars,
            "total_planets": total_planets,
            "total_life_worlds": total_life_worlds,
            "total_species": total_species,
            "total_civilizations": total_civilizations,
            "total_empires": total_empires,
            "total_wars": total_wars,
            "total_events": total_events,
            "simulation_years": max_year
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Register all modular API routers
app.include_router(stars_router)
app.include_router(planets_router)
app.include_router(species_router)
app.include_router(civilizations_router)
app.include_router(empires_router)
app.include_router(economy_router)
app.include_router(ftl_router)
app.include_router(wars_router)
app.include_router(history_router)
app.include_router(stories_router)
app.include_router(search_router)
app.include_router(analytics_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
