import re
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.api.stations import PROFILE_PATTERN, load_stations

router = APIRouter(prefix="/api/search", tags=["search"])

TOKEN_PATTERN = re.compile(r"[a-z0-9-]+")
STATION_ID_PATTERN = re.compile(r"ST-\d{4,5}", re.IGNORECASE)
STOP_WORDS = {
    "a",
    "an",
    "and",
    "around",
    "charger",
    "chargers",
    "charging",
    "ev",
    "find",
    "for",
    "near",
    "nearby",
    "please",
    "station",
    "stations",
    "the",
}
FAST_CHARGER_TERMS = {"fast", "quick", "rapid", "high", "power", "급속", "고속"}
REGION_ALIASES = {
    "seoul": "seoul",
    "서울": "seoul",
    "gyeonggi": "gyeonggi",
    "경기": "gyeonggi",
    "incheon": "incheon",
    "인천": "incheon",
}


class AskRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class AskResult(BaseModel):
    station_id: str
    name: str
    address: str
    region: str
    operator: str
    lat: float
    lng: float
    connector_count: int
    score: float
    matched_fields: list[str]


class AskResponse(BaseModel):
    message: str
    profile: str
    count: int
    mode: str
    results: list[AskResult]


def _tokens(message: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(message.lower()) if token not in STOP_WORDS]


def _normalized_station_id(message: str) -> str | None:
    match = STATION_ID_PATTERN.search(message)
    if not match:
        return None
    return match.group(0).upper()


def _text_blob(station: dict[str, Any]) -> str:
    values = [
        station.get("station_id", ""),
        station.get("name", ""),
        station.get("address", ""),
        station.get("region", ""),
        station.get("operator", ""),
    ]
    return " ".join(str(value).lower() for value in values)


def _score_station(station: dict[str, Any], message: str, tokens: list[str]) -> tuple[float, list[str]]:
    score = 0.0
    matched_fields: list[str] = []
    text_blob = _text_blob(station)
    lower_message = message.lower()
    station_id = str(station["station_id"])

    if _normalized_station_id(message) == station_id:
        score += 100.0
        matched_fields.append("station_id")

    for token in tokens:
        if token in text_blob:
            score += 5.0
            matched_fields.append("metadata")

    for alias, region in REGION_ALIASES.items():
        if alias in lower_message and str(station.get("region", "")).lower() == region:
            score += 12.0
            matched_fields.append("region")

    operator = str(station.get("operator", "")).lower()
    if operator and operator in lower_message:
        score += 10.0
        matched_fields.append("operator")

    if any(term in lower_message for term in FAST_CHARGER_TERMS):
        score += float(station.get("connector_count", 0))
        matched_fields.append("connector_count")

    return score, sorted(set(matched_fields))


def search_stations(message: str, *, profile: str, limit: int) -> tuple[str, list[AskResult]]:
    tokens = _tokens(message)
    scored: list[tuple[float, dict[str, Any], list[str]]] = []

    for station in load_stations(profile):
        score, matched_fields = _score_station(station, message, tokens)
        scored.append((score, station, matched_fields))

    positive = [item for item in scored if item[0] > 0]
    source = positive if positive else scored
    mode = "keyword" if positive else "fallback"
    source.sort(
        key=lambda item: (
            -item[0],
            -int(item[1].get("connector_count", 0)),
            str(item[1].get("station_id", "")),
        )
    )

    results = [
        AskResult(
            station_id=str(station["station_id"]),
            name=str(station["name"]),
            address=str(station["address"]),
            region=str(station["region"]),
            operator=str(station["operator"]),
            lat=float(station["lat"]),
            lng=float(station["lng"]),
            connector_count=int(station["connector_count"]),
            score=score,
            matched_fields=matched_fields,
        )
        for score, station, matched_fields in source[:limit]
    ]
    return mode, results


@router.post("/ask")
def ask(
    request: AskRequest,
    profile: str = Query(default="seoul-gyeonggi", pattern=PROFILE_PATTERN),
    limit: int = Query(default=5, ge=1, le=50),
) -> AskResponse:
    mode, results = search_stations(request.message, profile=profile, limit=limit)
    return AskResponse(
        message=request.message,
        profile=profile,
        count=len(results),
        mode=mode,
        results=results,
    )
