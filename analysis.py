"""Tested numerical functions; an agent chooses tools but never writes raster logic."""

from __future__ import annotations

from collections import defaultdict
from statistics import median

from models import Finding, Observation


MAX_CLOUD_FRACTION = 0.35


def usable_observations(observations: list[Observation]) -> tuple[list[Observation], list[Observation]]:
    usable = [item for item in observations if item.cloud_fraction <= MAX_CLOUD_FRACTION]
    rejected = [item for item in observations if item.cloud_fraction > MAX_CLOUD_FRACTION]
    return usable, rejected


def theil_sen(yearly_values: dict[int, float]) -> tuple[float, tuple[float, float]]:
    """Robust slope and a simple 10th–90th percentile slope interval."""
    years = sorted(yearly_values)
    slopes = [(yearly_values[later] - yearly_values[earlier]) / (later - earlier) for earlier in years for later in years if later > earlier]
    slopes.sort()
    if not slopes:
        raise ValueError("Need at least two yearly measurements for a trend.")
    lower = slopes[round((len(slopes) - 1) * 0.1)]
    upper = slopes[round((len(slopes) - 1) * 0.9)]
    return median(slopes), (lower, upper)


def detect_dry_season_change(
    observations: list[Observation], dry_months: tuple[int, ...] = (2, 3, 4, 5), window_years: int = 5
) -> Finding:
    usable, rejected = usable_observations(observations)
    by_year: dict[int, list[float]] = defaultdict(list)
    rain_by_year: dict[int, list[float]] = defaultdict(list)
    for item in usable:
        if item.observed_on.month in dry_months:
            by_year[item.observed_on.year].append(item.water_area_ha)
            rain_by_year[item.observed_on.year].append(item.rainfall_mm)
    years = sorted(year for year, values in by_year.items() if values)[-window_years:]
    if len(years) < 2:
        raise ValueError("Need usable dry-season observations from at least two years.")
    yearly_area = {year: median(by_year[year]) for year in years}
    yearly_rain = {year: sum(rain_by_year[year]) for year in years}
    slope, interval = theil_sen(yearly_area)
    rain_slope, _ = theil_sen(yearly_rain)
    first, last = years[0], years[-1]
    baseline = yearly_area[first]
    if baseline <= 0:
        raise ValueError("Baseline water area must be greater than zero; inspect the water mask.")
    recent = baseline + slope * (last - first)
    change = 100 * (recent - baseline) / baseline
    rainfall_declining = rain_slope < 0
    if change <= -10 and rainfall_declining:
        interpretation = "Dry-season water area declined; lower rainfall is consistent with part of the change."
    elif change <= -10:
        interpretation = "Dry-season water area declined; rainfall does not fully explain the signal."
    else:
        interpretation = "No material dry-season water-area decline was detected."
    dry_usable = [item for item in usable if item.observed_on.month in dry_months and item.observed_on.year in years]
    dry_rejected = [item for item in rejected if item.observed_on.month in dry_months and item.observed_on.year in years]
    count = len(dry_usable)
    confidence = "high" if count >= 10 and len(dry_rejected) <= count / 3 else "medium" if count >= 6 else "low"
    return Finding(baseline, recent, change, slope, interval, count, len(dry_rejected), len(years), confidence, interpretation)
