# simulation/history/significance_engine.py
"""Significance Engine for scoring and categorizing events.
Assigns impact scores (0-100) and significance classifications.
"""

from __future__ import annotations
from typing import Dict, Any
from ..utils import clamp, logger

class SignificanceEngine:
    """Calculates impact score and maps it to a significance level."""

    def __init__(self):
        # Base impact scores for different event types/categories
        self.base_scores = {
            "Trade Agreement": 5.0,
            "Economic Event": 5.0,
            "Transport Event": 2.0,
            "Alliance Formation": 15.0,
            "Defense Pact": 20.0,
            "Galactic Federation": 40.0,
            "War Declaration": 25.0,
            "War End": 20.0,
            "Peace Treaty Signing": 20.0,
            "Deep Space Engagement": 15.0,
            "Orbital Battle": 15.0,
            "System Defense": 15.0,
            "Planetary Invasion": 30.0,
            "Colony Assault": 25.0,
            "Megastructure Siege": 45.0,
            "Wormhole Assault": 35.0,
            "Jump Gate Defense": 30.0,
            "Technology Theft": 10.0,
            "Economic Sabotage": 12.0,
            "Industrial Espionage": 8.0,
            "Political Destabilization": 18.0,
            "Military Intelligence": 6.0,
            "Infrastructure Disruption": 14.0,
            "Counterintelligence": 5.0,
            "Great Galactic War": 90.0,
            "AI Uprising": 85.0,
            "Economic Collapse": 75.0,
            "Wormhole Collapse": 70.0,
            "FTL Network Failure": 80.0,
            "Resource Catastrophe": 65.0,
            "Pandemic Event": 60.0,
            "Megastructure Failure": 70.0,
            "Refugee Crisis": 55.0,
            "Political Fragmentation": 75.0,
            "Civilization Extinction": 100.0,
            "Empire Rebirth": 50.0,
            "Megastructure Completion": 60.0,
            "Colonization": 8.0,
            "Civilization Evolution": 10.0,
            "Scientific Breakthrough": 15.0,
            "Rise of Power": 30.0,
            "Peak Era": 40.0,
            "Decline Era": 25.0,
            "Collapse Era": 50.0,
        }

    def compute_significance(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates impact score and sets historical significance.
        Mutates the event dict in-place and returns it.
        """
        event_type = event.get("event_type", "")
        event_category = event.get("event_category", "")

        # 1. Resolve base score
        score = self.base_scores.get(event_type, self.base_scores.get(event_category, 5.0))

        # 2. Dynamic adjustments based on event details
        desc = event.get("description", "").lower()

        # Scale battles by casualties/losses
        if event_category == "Military" or "battle" in event_type.lower():
            # Extract casualties if mentioned in description
            # E.g. "Casualties: 1,500,000" or similar
            import re
            casualty_match = re.search(r"casualties:\s*([\d,]+)", desc)
            if casualty_match:
                try:
                    cas = int(casualty_match.group(1).replace(",", ""))
                    # Add log scale casualty bonus, e.g. ln(casualties)/2, max +30
                    import math
                    if cas > 0:
                        score += min(30.0, math.log(cas) * 1.5)
                except ValueError:
                    pass

            # Scale if war scale is mentioned
            if "scale: regional" in desc:
                score += 5
            elif "scale: galactic" in desc:
                score += 30
            elif "scale: sector" in desc:
                score += 15

        # Espionage success/damage scaling
        elif event_category == "Espionage":
            if "succeeded" in desc or "success: true" in desc:
                score += 5.0
            damage_match = re.search(r"damage(?: caused)?:\s*([\d\.]+)", desc)
            if damage_match:
                try:
                    dmg = float(damage_match.group(1))
                    score += min(15.0, dmg * 0.1)
                except ValueError:
                    pass

        # Economic event scaling
        elif event_category == "Economy":
            if "collapse" in desc or "crash" in desc:
                score += 30.0
            elif "boom" in desc or "expansion" in desc:
                score += 10.0

        # Clamp between 0 and 100
        score = clamp(score, 0.0, 100.0)
        event["impact_score"] = round(score, 2)

        # 3. Categorize historical significance
        if score < 15.0:
            event["historical_significance"] = "Minor"
        elif score < 40.0:
            event["historical_significance"] = "Significant"
        elif score < 70.0:
            event["historical_significance"] = "Major"
        elif score < 90.0:
            event["historical_significance"] = "Epochal"
        else:
            event["historical_significance"] = "Legendary"

        return event
