import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis import detect_dry_season_change, usable_observations
from demo_data import ambazari_demo_series
from models import Observation
from planner import plan_analysis
from stac import search_scenes


class MonitorTests(unittest.TestCase):
    def test_lake_question_uses_ndwi(self):
        self.assertEqual(plan_analysis("Has this lake shrunk?").index, "NDWI")

    def test_planner_scores_competing_keywords(self):
        self.assertEqual(plan_analysis("Has urban sprawl reduced green cover?").index, "NDBI")
        self.assertEqual(plan_analysis("Orange orchards near the lake").index, "NDVI")
        self.assertEqual(plan_analysis("Did the flood damage crops?").index, "NDVI")

    def test_cloudy_monsoon_observations_are_rejected(self):
        usable, rejected = usable_observations(ambazari_demo_series())
        self.assertEqual(len(rejected), 6)
        self.assertEqual(len(usable), 18)

    def test_demo_detects_dry_season_decline(self):
        finding = detect_dry_season_change(ambazari_demo_series())
        self.assertLess(finding.percent_change, -10)
        self.assertLess(finding.trend_ha_per_year, 0)
        self.assertIn("declined", finding.interpretation)

    def test_zero_baseline_has_actionable_error(self):
        observations = [
            Observation(date(2021, 3, 1), 0, 0, 10),
            Observation(date(2022, 3, 1), 1, 0, 10),
        ]
        with self.assertRaisesRegex(ValueError, "Baseline water area"):
            detect_dry_season_change(observations, window_years=2)

    def test_stac_network_error_has_actionable_error(self):
        with patch("stac.urlopen", side_effect=URLError("offline")):
            with self.assertRaisesRegex(RuntimeError, "STAC search failed"):
                search_scenes([79.02, 21.12, 79.04, 21.14], "2025-01-01/2025-12-31")


if __name__ == "__main__":
    unittest.main()
