# backend/api/history.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_db_connection

router = APIRouter(prefix="/api/history", tags=["History Center"])

@router.get("")
def get_history(
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Returns paginated list of historical simulation events, optionally filtered by category."""
    conn = get_db_connection()
    try:
        # Check if table exists (galactic_history_master)
        if category:
            query = "SELECT * FROM galactic_history_master WHERE event_category = ? ORDER BY year ASC LIMIT ? OFFSET ?"
            rows = conn.execute(query, (category, limit, offset)).fetchall()
        else:
            query = "SELECT * FROM galactic_history_master ORDER BY year ASC LIMIT ? OFFSET ?"
            rows = conn.execute(query, (limit, offset)).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/eras")
def get_eras():
    """Returns list of historical epochs / eras."""
    conn = get_db_connection()
    try:
        query = "SELECT * FROM era_history ORDER BY start_year ASC"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
