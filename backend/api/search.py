# backend/api/search.py
from fastapi import APIRouter, HTTPException
from database import get_db_connection

router = APIRouter(prefix="/api/search", tags=["Global Search"])

@router.get("")
def search_entities(q: str):
    """Unified global search across stars, planets, species, civilizations, empires, figures, events, stories, and news."""
    if not q or len(q) < 2:
        return {
            "stars": [], "planets": [], "species": [], 
            "civilizations": [], "empires": [], "figures": [], 
            "events": [], "stories": [], "news": []
        }
    
    conn = get_db_connection()
    term = f"%{q}%"
    results = {}
    
    try:
        # 1. Search Stars
        results["stars"] = [dict(row) for row in conn.execute(
            "SELECT * FROM stars WHERE name LIKE ? OR star_type LIKE ? LIMIT 10", (term, term)
        ).fetchall()]
        if not results["stars"]:
            results["stars"] = [dict(row) for row in conn.execute(
                "SELECT * FROM star_systems WHERE star_name LIKE ? OR star_type LIKE ? LIMIT 10", (term, term)
            ).fetchall()]
        
        # 2. Search Planets
        results["planets"] = [dict(row) for row in conn.execute(
            "SELECT * FROM planets WHERE planet_name LIKE ? OR planet_type LIKE ? LIMIT 10", (term, term)
        ).fetchall()]
        
        # 3. Search Species
        try:
            results["species"] = [dict(row) for row in conn.execute(
                "SELECT * FROM species_catalog WHERE name LIKE ? LIMIT 10", (term,)
            ).fetchall()]
        except Exception:
            results["species"] = []
            
        # 4. Search Civilizations
        try:
            results["civilizations"] = [dict(row) for row in conn.execute(
                "SELECT * FROM civilizations WHERE name LIKE ? LIMIT 10", (term,)
            ).fetchall()]
        except Exception:
            results["civilizations"] = []
            
        # 5. Search Empires
        try:
            results["empires"] = [dict(row) for row in conn.execute(
                "SELECT * FROM empires WHERE empire_name LIKE ? OR capital_world LIKE ? LIMIT 10", (term, term)
            ).fetchall()]
        except Exception:
            results["empires"] = []
            
        # 6. Search Figures
        try:
            results["figures"] = [dict(row) for row in conn.execute(
                "SELECT * FROM historical_figures WHERE name LIKE ? OR role LIKE ? LIMIT 10", (term, term)
            ).fetchall()]
        except Exception:
            results["figures"] = []
            
        # 7. Search Events
        try:
            results["events"] = [dict(row) for row in conn.execute(
                "SELECT * FROM galactic_history_master WHERE event_type LIKE ? OR description LIKE ? LIMIT 10", (term, term)
            ).fetchall()]
        except Exception:
            results["events"] = []
            
        # 8. Search Stories
        try:
            results["stories"] = [dict(row) for row in conn.execute(
                "SELECT * FROM legendary_stories WHERE prose_narrative LIKE ? OR empire_involved LIKE ? LIMIT 10", (term, term)
            ).fetchall()]
        except Exception:
            results["stories"] = []
            
        # 9. Search News
        try:
            results["news"] = [dict(row) for row in conn.execute(
                "SELECT * FROM galactic_news WHERE headline LIKE ? OR body LIKE ? LIMIT 10", (term, term)
            ).fetchall()]
        except Exception:
            results["news"] = []
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
