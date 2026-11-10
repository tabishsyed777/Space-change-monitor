"""A transparent, deterministic lake series for offline demonstrations."""

from __future__ import annotations

from datetime import date

from models import Observation


def ambazari_demo_series() -> list[Observation]:
    observations = []
    for year in range(2021, 2027):
        dry_area = 185 - (year - 2021) * 5.0
        rainfall = 18 if year in (2023, 2024) else 35
        for month in (3, 5, 8, 11):
            seasonal_bonus = 42 if month == 8 else 15 if month == 11 else 0
            cloud = 0.62 if month == 8 else 0.12
            observations.append(Observation(date(year, month, 15), dry_area + seasonal_bonus, cloud, rainfall))
    return observations
