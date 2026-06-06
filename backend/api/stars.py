# backend/api/stars.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from database import get_db_connection

router = APIRouter(prefix="/api/stars", tags=["Stars"])

@router.get("")
def get_stars(limit: Optional[int] = None):
    """Returns all star systems with coordinates and details."""
    conn = get_db_connection()
    try:
        query = "SELECT * FROM stars"
        if limit:
            query += f" LIMIT {limit}"
        stars = conn.execute(query).fetchall()
        if not stars:
            # Fallback to star_systems if stars is empty
            query = "SELECT * FROM star_systems"
            if limit:
                query += f" LIMIT {limit}"
            stars = conn.execute(query).fetchall()
        return [dict(row) for row in stars]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/{star_id}")
def get_star(star_id: str):
    """Returns details for a single star system."""
    conn = get_db_connection()
    try:
        # Check both id column and star_id column as fallback
        row = conn.execute("SELECT * FROM stars WHERE id = ?", (star_id,)).fetchone()
        if not row:
            row = conn.execute("SELECT * FROM stars WHERE star_id = ?", (star_id,)).fetchone()
        if not row:
            row = conn.execute("SELECT * FROM star_systems WHERE star_id = ?", (star_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Star system not found")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
