# backend/api/empires.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_db_connection

router = APIRouter(prefix="/api/empires", tags=["Empires"])

@router.get("")
def get_empires(limit: int = 100):
    """Returns list of empires with population, GDP, and capital world."""
    conn = get_db_connection()
    try:
        query = f"SELECT * FROM empires LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/chronicles")
def get_chronicles(empire_name: Optional[str] = None):
    """Returns narrative chronicles for empires, optionally filtered by empire_name."""
    conn = get_db_connection()
    try:
        if empire_name:
            query = "SELECT * FROM empire_chronicles WHERE empire_name = ?"
            rows = conn.execute(query, (empire_name,)).fetchall()
        else:
            query = "SELECT * FROM empire_chronicles LIMIT 50"
            rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/lifecycles")
def get_lifecycles(empire_name: Optional[str] = None):
    """Returns historical lifecycle stage transitions for empires."""
    conn = get_db_connection()
    try:
        if empire_name:
            query = "SELECT * FROM empire_lifecycles WHERE empire_name = ? ORDER BY year ASC"
            rows = conn.execute(query, (empire_name,)).fetchall()
        else:
            query = "SELECT * FROM empire_lifecycles ORDER BY year ASC LIMIT 100"
            rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
