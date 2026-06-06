# backend/api/wars.py
from fastapi import APIRouter, HTTPException
from database import get_db_connection

router = APIRouter(prefix="/api/wars", tags=["Diplomacy & Warfare"])

@router.get("")
def get_wars(limit: int = 100):
    """Returns historical wars catalog."""
    conn = get_db_connection()
    try:
        query = f"SELECT * FROM wars LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/reports")
def get_war_reports(limit: int = 50):
    """Returns detailed war logs and impact summaries."""
    conn = get_db_connection()
    try:
        query = f"SELECT * FROM war_reports LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/battles")
def get_battles(limit: int = 100):
    """Returns direct dreadnought and fleet engagements."""
    conn = get_db_connection()
    try:
        query = f"SELECT * FROM battles LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/treaties")
def get_peace_treaties():
    """Returns signed peace treaties."""
    conn = get_db_connection()
    try:
        query = "SELECT * FROM peace_treaties"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
