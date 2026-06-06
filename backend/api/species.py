# backend/api/species.py
from fastapi import APIRouter, HTTPException
from database import get_db_connection

router = APIRouter(prefix="/api/species", tags=["Species"])

@router.get("")
def get_species(limit: int = 500):
    """Returns species list from species catalog."""
    conn = get_db_connection()
    try:
        # Check both species_catalog and life_catalog as backup
        query = f"SELECT * FROM species_catalog LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        if not rows:
            # Fallback to life_catalog filtering for complex/intelligent life
            query = f"SELECT * FROM life_catalog WHERE species_complexity > 0 LIMIT {limit}"
            rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
