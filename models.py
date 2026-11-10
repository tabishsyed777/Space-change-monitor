"""Typed, auditable records exchanged by the monitoring pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal


IndexName = Literal["NDVI", "NDWI", "NDBI", "NBR"]


@dataclass(frozen=True)
class Plan:
    objective: str
    index: IndexName
    baseline_years: int
    needs_weather: bool
    notes: tuple[str, ...]


@dataclass(frozen=True)
class Observation:
    observed_on: date
    water_area_ha: float
    cloud_fraction: float
    rainfall_mm: float
    source: str = "demo"


@dataclass(frozen=True)
class Finding:
    baseline_ha: float
    recent_ha: float
    percent_change: float
    trend_ha_per_year: float
    trend_interval_ha_per_year: tuple[float, float]
    usable_observations: int
    rejected_observations: int
    dry_season_years: int
    confidence: Literal["low", "medium", "high"]
    interpretation: str
