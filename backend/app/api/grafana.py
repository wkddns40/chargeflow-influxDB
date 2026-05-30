from urllib.parse import urlencode

from fastapi import APIRouter, Query

from app.core.config import get_settings

router = APIRouter(prefix="/api/grafana", tags=["grafana"])


@router.get("/station-timeline-url")
def station_timeline_url(station_id: str = Query(pattern=r"^ST-\d{4,5}$")) -> dict[str, str]:
    settings = get_settings()
    query = urlencode(
        {
            "orgId": "1",
            "var-station_id": station_id,
            "from": "now-24h",
            "to": "now",
            "kiosk": "",
        }
    )
    base = settings.grafana_base_url.rstrip("/")
    return {"station_id": station_id, "url": f"{base}/d/station-24h/station-24h?{query}"}
