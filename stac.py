"""Small STAC scene-discovery adapter; raster processing is intentionally separate."""

from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen


EARTH_SEARCH_URL = "https://earth-search.aws.element84.com/v1/search"


def search_scenes(bbox: list[float], date_range: str, max_cloud: float = 35.0, limit: int = 20) -> list[dict]:
    """Search Sentinel-2 L2A metadata without downloading image pixels."""
    if len(bbox) != 4:
        raise ValueError("bbox must be [west, south, east, north]")
    payload = {
        "collections": ["sentinel-2-l2a"],
        "bbox": bbox,
        "datetime": date_range,
        "query": {"eo:cloud_cover": {"lte": max_cloud}},
        "limit": limit,
    }
    request = Request(EARTH_SEARCH_URL, json.dumps(payload).encode(), {"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode())
    except (URLError, OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("STAC search failed; check connectivity, endpoint availability, and query bounds.") from exc
    if not isinstance(body, dict):
        raise RuntimeError("STAC search returned an unexpected response.")
    return [
        {"id": feature["id"], "datetime": feature["properties"].get("datetime"), "cloud_cover": feature["properties"].get("eo:cloud_cover")}
        for feature in body.get("features", [])
    ]
