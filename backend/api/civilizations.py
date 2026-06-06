# backend/api/civilizations.py
from fastapi import APIRouter, HTTPException
from database import get_db_connection

router = APIRouter(prefix="/api/civilizations", tags=["Civilizations"])

@router.get("")
def get_civilizations(limit: int = 500):
    """Returns civilizations from civilizations list."""
    conn = get_db_connection()
    try:
        query = f"SELECT * FROM civilizations LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
