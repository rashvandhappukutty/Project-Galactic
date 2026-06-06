# backend/api/ftl.py
from fastapi import APIRouter, HTTPException
from database import get_db_connection

router = APIRouter(prefix="/api/ftl", tags=["FTL Infrastructure"])

@router.get("")
def get_ftl_routes(limit: int = 500):
    """Returns interstellar FTL hyperlane networks and jump gate routes."""
    conn = get_db_connection()
    try:
        # Check ftl_routes table
        query = f"SELECT * FROM ftl_routes LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        if not rows:
            # Fallback to hyperlane_network
            query = f"SELECT * FROM hyperlane_network LIMIT {limit}"
            rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/gates")
def get_jump_gates(limit: int = 200):
    """Returns established jump gate anchors."""
    conn = get_db_connection()
    try:
        query = f"SELECT * FROM jump_gates LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/wormholes")
def get_wormholes():
    """Returns mapped wormhole sub-space rifts and coordinates."""
    conn = get_db_connection()
    try:
        query = "SELECT * FROM wormholes"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
