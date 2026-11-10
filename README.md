# Space Change Monitor

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Stage](https://img.shields.io/badge/Stage-Lake%20monitoring%20MVP-1f6feb)
![Data](https://img.shields.io/badge/Data-Sentinel--2%20STAC%20discovery-2ea44f)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

An evidence-first **lake-monitoring skeleton** for a future agent that watches a place from space and explains what changed, when it changed, how large the change is, and what context might explain it.

The first version focuses on lake shrinkage. Given a question such as “Has Ambazari Lake’s water area changed over the last five years?”, deterministic planning code selects an analysis plan, filters cloud-contaminated observations, compares like-for-like dry-season measurements, and writes a caveated report. It does **not** yet process satellite pixels or run an LLM/tool loop.

## What works now

- A planner selects the primary remote-sensing index: NDWI for water, NDVI for vegetation, and NDBI for built-up change.
- A tested change detector excludes cloudy observations and compares the same dry-season months across years.
- Trend interpretation uses rainfall only as context—never as proof of cause.
- A deterministic Ambazari-style demo works without credentials, imagery downloads, or third-party packages; its measurements are intentionally synthetic.
- An optional live STAC search discovers Sentinel-2 L2A scene metadata from Earth Search; it does not download raster pixels.

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/tabishsyed777/Space-change-monitor.git
cd Space-change-monitor
python -m unittest discover -s tests -v
python main.py --demo
```

The demo reports a synthetic dry-season decline and rejects intentionally cloud-contaminated monsoon observations. It proves the workflow and tests, not a real finding about Ambazari Lake.

## Optional live scene discovery

With internet access, search Sentinel-2 L2A metadata for a small bounding box:

```bash
python main.py --stac-search --bbox 79.02,21.12,79.04,21.14
```

Earth Search’s STAC endpoint is `https://earth-search.aws.element84.com/v1`; it indexes cloud-native Sentinel-2 L2A data. The catalog is used only for discovery in this MVP. [Earth Search documentation](https://element84.com/earth-search/examples/) and [NASA POWER daily API documentation](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) describe the planned production data sources.

## Agent workflow

```text
Question + region
   ↓
Planner → selects index, season, baseline, and context checks
   ↓
Data scout → searches STAC metadata and rejects unsuitable scenes
   ↓
Processing tools → cloud mask, composite, index, water-area estimate
   ↓
Verifier → tests seasonality, cloud artifacts, and weather context
   ↓
Report → numbers, confidence, caveats, and before/after evidence
```

The diagram describes the target agent architecture. The code currently implements only deterministic planning, quality filtering, trend analysis, reporting, and STAC metadata discovery. A future LLM planner may select tools and interpret structured results, but it must not generate raster-processing code or make unsupported claims.

## Roadmap to real imagery analysis

1. Load Sentinel-2 Cloud-Optimized GeoTIFF assets with `pystac-client` and `stackstac`.
2. Apply Sentinel-2 Scene Classification Layer cloud/shadow masking and monthly median compositing.
3. Compute NDWI water masks and calibrated area statistics from pixel counts.
4. Add Sentinel-1 SAR for cloudy monsoon months and NASA POWER/CHIRPS for weather context.
5. Render before/after tiles, add a map UI, cache outputs, and evaluate against hand labels and documented events.

## Limitations

- The current demo uses synthetic observations; it does not yet derive NDWI or water area from imagery.
- Sentinel-2’s 10 m resolution limits small-feature and shoreline accuracy.
- A lower water area can be consistent with rainfall or management conditions; it does not prove a cause.
- Production deployment must enforce scene-quality checks, same-season baselines, source citations, and area limits.

## Interpreting results responsibly

The report’s confidence describes observation coverage and cloud filtering, not certainty about a real-world cause. Treat detected change as a screening signal. Verify it with rendered imagery, same-season comparisons, ground knowledge, and—where applicable—rainfall and radar observations before making a decision.

## Project layout

```text
space_change_monitor/
├── planner.py       # Chooses index and evidence plan
├── stac.py          # Sentinel-2 metadata discovery
├── analysis.py      # Deterministic, tested change calculations
├── report.py        # Evidence-first Markdown reporting
├── demo_data.py     # Reproducible offline observations
└── tests/           # Planner, cloud-filter, and trend tests
```

## License

MIT License.
