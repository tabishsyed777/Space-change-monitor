"""The judgement layer: choose analysis primitives from a user question."""

from __future__ import annotations

from models import Plan


def plan_analysis(question: str) -> Plan:
    text = question.lower()
    scores = {"water": 0, "vegetation": 0, "built_up": 0}
    weights = {
        "water": (("lake", 2), ("reservoir", 2), ("water", 2), ("flood", 1), ("shrink", 1)),
        "vegetation": (("orchard", 3), ("orange", 2), ("crop", 3), ("vegetation", 2), ("forest", 2), ("green cover", 2)),
        "built_up": (("urban sprawl", 3), ("built-up", 3), ("construction", 2), ("metro", 2), ("urban", 1), ("sprawl", 2)),
    }
    for category, terms in weights.items():
        scores[category] = sum(weight for term, weight in terms if term in text)
    # In a tie, the more specific land-cover objectives outrank contextual water words.
    category = max(scores, key=lambda name: (scores[name], {"vegetation": 2, "built_up": 1, "water": 0}[name]))
    if scores[category] == 0:
        category = "vegetation"
    if category == "water":
        return Plan(
            objective="measure water-surface change",
            index="NDWI",
            baseline_years=5,
            needs_weather=True,
            notes=(
                "Compare the same season across years to avoid seasonal water-level bias.",
                "Reject cloud-contaminated optical observations; use radar in a production monsoon workflow.",
            ),
        )
    if category == "vegetation":
        return Plan("measure vegetation condition", "NDVI", 5, True, ("Use seasonal baselines.",))
    if category == "built_up":
        return Plan("measure built-up expansion", "NDBI", 3, False, ("Validate against clouds and bare soil.",))
