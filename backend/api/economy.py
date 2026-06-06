# backend/api/economy.py
from fastapi import APIRouter, HTTPException
from typing import Optional
from database import get_db_connection

router = APIRouter(prefix="/api/economy", tags=["Economy"])

@router.get("")
def get_economy(limit: int = 200):
    """Returns economic statistics, GDP, resources, and tax rates of civilizations."""
    conn = get_db_connection()
    try:
        # Check if economy table exists, else fallback to civilizations
        query = f"SELECT * FROM economy LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception:
        try:
            query = f"SELECT empire_name, gdp, population FROM empires LIMIT {limit}"
            rows = conn.execute(query).fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/blocs")
def get_economic_blocs():
    """Returns economic alliances and trade federations."""
    conn = get_db_connection()
    try:
        query = "SELECT * FROM economic_blocs"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/prices")
def get_market_prices(limit: int = 100):
    """Returns historical resource market trading prices."""
    conn = get_db_connection()
    try:
        query = f"SELECT * FROM market_prices LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
