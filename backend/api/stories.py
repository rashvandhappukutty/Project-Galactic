# backend/api/stories.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_db_connection

router = APIRouter(prefix="/api/stories", tags=["Stories Portal"])

@router.get("")
def get_legendary_stories(limit: int = 50):
    """Returns list of legendary stories / sagas."""
    conn = get_db_connection()
    try:
        query = f"SELECT * FROM legendary_stories LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/news")
def get_news(limit: int = Query(50, ge=1, le=100)):
    """Returns GNN breaking news articles."""
    conn = get_db_connection()
    try:
        query = f"SELECT * FROM galactic_news ORDER BY year DESC LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/lore")
def get_lore():
    """Returns ancient myths, archives, and lore entries."""
    conn = get_db_connection()
    try:
        query = "SELECT * FROM galactic_lore"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
