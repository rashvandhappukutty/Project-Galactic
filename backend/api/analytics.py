# backend/api/analytics.py
from fastapi import APIRouter, HTTPException
from database import get_db_connection

router = APIRouter(prefix="/api/analytics", tags=["Live Analytics"])

@router.get("")
def get_analytics():
    """Returns general leaderboards across economics and power scales."""
    conn = get_db_connection()
    try:
        # Top 10 GDP Empires
        top_gdp = [dict(row) for row in conn.execute(
            "SELECT empire_name, gdp, population FROM empires ORDER BY gdp DESC LIMIT 10"
        ).fetchall()]
        
        # Top 10 Militaries / Power Index
        top_military = [dict(row) for row in conn.execute(
            "SELECT empire_name, power_index, colonies_count FROM empires ORDER BY power_index DESC LIMIT 10"
        ).fetchall()]
        
        return {
            "top_gdp": top_gdp,
            "top_military": top_military
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/figures")
def get_historical_figures(limit: int = 50):
    """Returns notable historical figures list with legacy scores."""
    conn = get_db_connection()
    try:
        query = f"SELECT * FROM historical_figures ORDER BY legacy_score DESC LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
