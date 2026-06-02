from math import asin, cos, radians, sin, sqrt
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
PLACE_ALIASES = {
    "gangnam": (37.5172, 127.0473),
    "gangnam-gu office": (37.5172, 127.0473),
    "강남구청": (37.5172, 127.0473),
    "강남": (37.4979, 127.0276),
    "seocho": (37.4919, 127.0079),
    "seocho station": (37.4919, 127.0079),
    "서초": (37.4919, 127.0079),
    "서초역": (37.4919, 127.0079),
    "서울시청": (37.5665, 126.9780),
    "seoul city hall": (37.5665, 126.9780),
    "잠실": (37.5133, 127.1000),
    "jamsil": (37.5133, 127.1000),
    "mapo": (37.5600, 126.9125),
    "마포": (37.5600, 126.9125),
    "seongdong": (37.5550, 127.0425),
    "성동": (37.5550, 127.0425),
    "yongsan": (37.5299, 126.9648),
    "yongsan station": (37.5299, 126.9648),
    "용산": (37.5299, 126.9648),
    "용산역": (37.5299, 126.9648),
    "jongno": (37.5780, 126.9825),
    "종로": (37.5780, 126.9825),
    "guro": (37.4970, 126.8890),
    "구로": (37.4970, 126.8890),
    "nowon": (37.6560, 127.0600),
    "노원": (37.6560, 127.0600),
    "판교": (37.3948, 127.1112),
    "pangyo": (37.3948, 127.1112),
    "수원": (37.2636, 127.0286),
    "suwon": (37.2636, 127.0286),
    "인천": (37.4563, 126.7052),
    "incheon": (37.4563, 126.7052),
    "bupyeong": (37.5040, 126.7175),
    "부평": (37.5040, 126.7175),
    "songdo": (37.3825, 126.6575),
    "송도": (37.3825, 126.6575),
    "cheongna": (37.5325, 126.6475),
    "청라": (37.5325, 126.6475),
    "고양": (37.6584, 126.8320),
    "goyang": (37.6584, 126.8320),
    "성남": (37.4202, 127.1265),
    "seongnam": (37.4202, 127.1265),
    "용인": (37.2411, 127.1776),
    "yongin": (37.2411, 127.1776),
    "bucheon": (37.5000, 126.7685),
    "부천": (37.5000, 126.7685),
    "ansan": (37.3200, 126.8360),
    "안산": (37.3200, 126.8360),
    "anyang": (37.3950, 126.9590),
    "안양": (37.3950, 126.9590),
    "uijeongbu": (37.7415, 127.0400),
    "의정부": (37.7415, 127.0400),
    "namyangju": (37.6385, 127.2125),
    "남양주": (37.6385, 127.2125),
    "hanam": (37.5420, 127.2125),
    "하남": (37.5420, 127.2125),
    "gimpo": (37.6165, 126.7175),
    "김포": (37.6165, 126.7175),
    "gwangmyeong": (37.4790, 126.8625),
    "광명": (37.4790, 126.8625),
    "siheung": (37.3825, 126.8025),
    "시흥": (37.3825, 126.8025),
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
    max_kw: float = 50.0
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


def _matched_place(message: str) -> tuple[float, float] | None:
    lower_message = message.lower()
    for alias, coordinates in PLACE_ALIASES.items():
        if alias in lower_message:
            return coordinates
    return None


def _distance_km(station: dict[str, Any], target: tuple[float, float]) -> float:
    station_lat = radians(float(station["lat"]))
    station_lng = radians(float(station["lng"]))
    target_lat = radians(target[0])
    target_lng = radians(target[1])
    lat_delta = target_lat - station_lat
    lng_delta = target_lng - station_lng
    haversine = sin(lat_delta / 2) ** 2 + cos(station_lat) * cos(target_lat) * sin(lng_delta / 2) ** 2
    return 6371.0 * 2 * asin(sqrt(haversine))


def _text_blob(station: dict[str, Any]) -> str:
    values = [
        station.get("station_id", ""),
        station.get("name", ""),
        station.get("address", ""),
        station.get("region", ""),
        station.get("operator", ""),
    ]
    return " ".join(str(value).lower() for value in values)


def _score_station(
    station: dict[str, Any],
    message: str,
    tokens: list[str],
    target: tuple[float, float] | None,
) -> tuple[float, list[str]]:
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

    if target:
        distance_km = _distance_km(station, target)
        score += max(1.0, 200.0 - distance_km * 8.0)
        matched_fields.append("location")

    return score, sorted(set(matched_fields))


def search_stations(message: str, *, profile: str, limit: int) -> tuple[str, list[AskResult]]:
    tokens = _tokens(message)
    target = _matched_place(message)
    scored: list[tuple[float, dict[str, Any], list[str]]] = []

    for station in load_stations(profile):
        score, matched_fields = _score_station(station, message, tokens, target)
        scored.append((score, station, matched_fields))

    positive = [item for item in scored if item[0] > 0]
    source = positive if positive else scored
    mode = "location" if target else "keyword" if positive else "fallback"
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
            max_kw=float(station.get("max_kw", 50.0)),
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
    limit: int = Query(default=3, ge=1, le=50),
) -> AskResponse:
    mode, results = search_stations(request.message, profile=profile, limit=limit)
    return AskResponse(
        message=request.message,
        profile=profile,
        count=len(results),
        mode=mode,
        results=results,
    )
