"""Evidence-first report generation from structured findings only."""

from __future__ import annotations

from models import Finding, Plan


def render_report(place: str, question: str, plan: Plan, finding: Finding) -> str:
    direction = "decreased" if finding.percent_change < 0 else "increased"
    return f"""# Space Change Monitor report

## Question

{question}

## Analysis plan

- Region: {place}
- Objective: {plan.objective}
- Primary index: {plan.index}
- Baseline design: same-season trend across {finding.dry_season_years} available years (requested window: {plan.baseline_years})

## Evidence

- Baseline dry-season water area: **{finding.baseline_ha:.1f} ha**
- Most recent dry-season water area: **{finding.recent_ha:.1f} ha**
- Estimated change: **{finding.percent_change:.1f}%** ({direction})
- Robust trend: **{finding.trend_ha_per_year:.2f} ha/year** (pairwise-slope interval: {finding.trend_interval_ha_per_year[0]:.2f} to {finding.trend_interval_ha_per_year[1]:.2f})
- Usable observations: {finding.usable_observations}; cloud-rejected observations: {finding.rejected_observations}

## Interpretation

{finding.interpretation}

## Confidence and caveats

Confidence: **{finding.confidence}**. This report compares the same dry-season months and excludes scenes with more than 35% cloud cover. It shows a satellite-derived association, not proof of cause. A production result should include cloud-masked Sentinel-2 composites, Sentinel-1 radar during monsoon, and before/after map tiles.
"""
