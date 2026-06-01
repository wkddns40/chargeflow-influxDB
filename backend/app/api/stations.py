import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from app.core.config import get_settings

router = APIRouter(prefix="/api/stations", tags=["stations"])
PROFILE_PATTERN = "^(smoke|seoul-gyeonggi|dev|perf)$"


def _station_file(profile: str) -> Path:
    return get_settings().data_dir / f"stations_{profile}.json"


def load_stations(profile: str = "smoke") -> list[dict]:
    path = _station_file(profile)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("")
def list_stations(
    profile: str = Query(default="seoul-gyeonggi", pattern=PROFILE_PATTERN),
    limit: int = Query(default=700, ge=1, le=10000),
) -> dict[str, object]:
    stations = load_stations(profile)
    return {"profile": profile, "count": len(stations[:limit]), "stations": stations[:limit]}


@router.get("/{station_id}")
def get_station(
    station_id: str,
    profile: str = Query(default="seoul-gyeonggi", pattern=PROFILE_PATTERN),
) -> dict:
    for station in load_stations(profile):
        if station["station_id"] == station_id:
            return station
    raise HTTPException(status_code=404, detail="station not found")
