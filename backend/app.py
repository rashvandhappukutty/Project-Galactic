# backend/app.py
"""FastAPI Backend Server for Phase 12 - Living Galactic Digital Twin.
Loads all Phase 1-11 CSV files dynamically into SQLite database,
and exposes REST endpoints using modular API routers.
"""

from __future__ import annotations
import os
import glob
import sqlite3
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import modular API routers
from api.stars import router as stars_router
from api.planets import router as planets_router
from api.civilizations import router as civilizations_router
from api.history import router as history_router
from api.stories import router as stories_router
from api.wars import router as wars_router
from api.analytics import router as analytics_router

app = FastAPI(title="The Galactic Dream Engine - Digital Twin API")

# Setup CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "galactic_twin.db"
DATASETS_DIR = "datasets"

def init_database():
    """Reads all CSV files from datasets/ and writes them into SQLite tables."""
    print("Initializing SQLite Database from CSV files...")
    conn = sqlite3.connect(DB_PATH)
    
    # Check fallback path
    dir_to_use = DATASETS_DIR
    if not os.path.exists(dir_to_use) and os.path.exists(os.path.join("..", DATASETS_DIR)):
        dir_to_use = os.path.join("..", DATASETS_DIR)
        
    csv_files = glob.glob(os.path.join(dir_to_use, "*.csv"))
    if not csv_files:
        print(f"Warning: No datasets found in '{dir_to_use}'. Please run earlier simulation phases.")
        return

    for file_path in csv_files:
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            df = pd.read_csv(file_path)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"  - Loaded table '{table_name}' ({len(df)} rows)")
        except Exception as e:
            print(f"  - Error loading '{table_name}': {e}")
            
    conn.close()
    print("Database initialization complete.")

@app.on_event("startup")
def startup_event():
    init_database()

# Register all modular API routers
app.include_router(stars_router)
app.include_router(planets_router)
app.include_router(civilizations_router)
app.include_router(history_router)
app.include_router(stories_router)
app.include_router(wars_router)
app.include_router(analytics_router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
