"""CLI for the lake-change MVP."""

from __future__ import annotations

import argparse

from analysis import detect_dry_season_change
from demo_data import ambazari_demo_series
from planner import plan_analysis
from report import render_report
from stac import search_scenes


def main() -> None:
    parser = argparse.ArgumentParser(description="Evidence-first satellite change monitor MVP.")
    parser.add_argument("--question", default="Has Ambazari Lake's water area changed over the last 5 years?")
    parser.add_argument("--place", default="Ambazari Lake, Nagpur")
    parser.add_argument("--demo", action="store_true", help="Run the deterministic lake-monitoring demonstration.")
    parser.add_argument("--stac-search", action="store_true", help="Search Sentinel-2 scene metadata only.")
    parser.add_argument("--bbox", default="79.02,21.12,79.04,21.14", help="west,south,east,north for STAC search")
    parser.add_argument("--date-range", default="2025-01-01/2025-12-31", help="STAC ISO-8601 interval")
    args = parser.parse_args()
    if args.stac_search:
        bbox = [float(value) for value in args.bbox.split(",")]
        for scene in search_scenes(bbox, args.date_range):
            print(scene)
        return
    if not args.demo:
        raise SystemExit("Start with --demo, or use --stac-search for live scene discovery.")
    plan = plan_analysis(args.question)
    if plan.index != "NDWI":
        raise SystemExit(f"This lake MVP only measures water with NDWI; the planner selected {plan.index}. Use a water question or add the corresponding pixel processor.")
    finding = detect_dry_season_change(ambazari_demo_series(), window_years=plan.baseline_years)
    print(render_report(args.place, args.question, plan, finding))


if __name__ == "__main__":
    main()
