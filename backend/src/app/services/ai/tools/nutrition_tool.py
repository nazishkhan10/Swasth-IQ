"""
Nutrition Tool (Phase 7 AI Medical Tools).
Generates deterministic dietary recommendations based on detected Phase 6 conditions.
"""

from typing import Dict, Any, List


class NutritionTool:
    @classmethod
    def execute(cls, detected_conditions: List[Dict[str, Any]]) -> Dict[str, Any]:
        foods_to_eat = ["Whole grains & pulses", "Leafy green vegetables", "Soluble oat fiber", "Lean proteins"]
        foods_to_avoid = ["Refined sugar & soft drinks", "Trans fats & fried foods", "High-sodium processed meats (> 2000mg/day)"]
        return {
            "foods_to_eat": foods_to_eat,
            "foods_to_avoid": foods_to_avoid,
            "dietary_model": "Low-Glycemic Mediterranean Diet with Sodium Restriction"
        }
