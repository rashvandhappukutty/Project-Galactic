# backend/api/planets.py
from fastapi import APIRouter, HTTPException
from typing import Optional
from database import get_db_connection

router = APIRouter(prefix="/api/planets", tags=["Planets"])

@router.get("")
def get_planets(star_id: Optional[str] = None, limit: int = 500):
    """Returns planets, optionally filtered by star_id."""
    conn = get_db_connection()
    try:
        if star_id:
            query = "SELECT * FROM planets WHERE star_id = ?"
            planets = conn.execute(query, (star_id,)).fetchall()
        else:
            query = f"SELECT * FROM planets LIMIT {limit}"
            planets = conn.execute(query).fetchall()
        return [dict(row) for row in planets]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/{planet_id}")
def get_planet(planet_id: str):
    """Returns details for a single planet."""
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM planets WHERE planet_id = ?", (planet_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Planet not found")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
