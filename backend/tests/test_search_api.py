from fastapi.testclient import TestClient

from app.api.search import PLACE_ALIASES
from app.main import app
from tools.mockgen import SEOUL_GYEONGGI_STATION_AREAS


EXPECTED_AREA_ALIASES = {
    "Gangnam": {"gangnam", "강남"},
    "Seocho": {"seocho", "서초"},
    "Jamsil": {"jamsil", "잠실"},
    "Mapo": {"mapo", "마포"},
    "Seongdong": {"seongdong", "성동"},
    "Yongsan": {"yongsan", "용산", "용산역"},
    "Jongno": {"jongno", "종로"},
    "Guro": {"guro", "구로"},
    "Nowon": {"nowon", "노원"},
    "Bupyeong": {"bupyeong", "부평"},
    "Songdo": {"songdo", "송도"},
    "Cheongna": {"cheongna", "청라"},
    "Suwon": {"suwon", "수원"},
    "Seongnam": {"seongnam", "성남"},
    "Yongin": {"yongin", "용인"},
    "Goyang": {"goyang", "고양"},
    "Bucheon": {"bucheon", "부천"},
    "Ansan": {"ansan", "안산"},
    "Anyang": {"anyang", "안양"},
    "Uijeongbu": {"uijeongbu", "의정부"},
    "Namyangju": {"namyangju", "남양주"},
    "Hanam": {"hanam", "하남"},
    "Gimpo": {"gimpo", "김포"},
    "Gwangmyeong": {"gwangmyeong", "광명"},
    "Siheung": {"siheung", "시흥"},
}


def test_place_aliases_cover_station_area_bboxes() -> None:
    station_areas = {area for _, area, *_ in SEOUL_GYEONGGI_STATION_AREAS}

    assert station_areas == set(EXPECTED_AREA_ALIASES)
    for area in station_areas:
        assert EXPECTED_AREA_ALIASES[area] <= set(PLACE_ALIASES)


def test_ask_api_returns_station_results_without_llm_secret() -> None:
    response = TestClient(app).post(
        "/api/search/ask",
        json={"message": "Gangnam fast charger"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["profile"] == "seoul-gyeonggi"
    assert body["count"] > 0
    assert body["results"][0]["station_id"].startswith("ST-")
    assert "connector_count" in body["results"][0]["matched_fields"]


def test_ask_api_matches_station_id() -> None:
    response = TestClient(app).post(
        "/api/search/ask",
        json={"message": "show ST-0001 timeline"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["mode"] == "keyword"
    assert body["results"][0]["station_id"] == "ST-0001"
    assert "station_id" in body["results"][0]["matched_fields"]


def test_ask_api_matches_region_and_limit() -> None:
    response = TestClient(app).post(
        "/api/search/ask?limit=3",
        json={"message": "Seoul ChargeFlow"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["count"] == 3
    assert all(result["region"] == "Seoul" for result in body["results"])


def test_ask_api_uses_place_distance_for_korean_location() -> None:
    response = TestClient(app).post(
        "/api/search/ask?limit=5",
        json={"message": "강남구청에서 가장 가까운 충전소"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["mode"] == "location"
    assert body["count"] == 5
    assert "location" in body["results"][0]["matched_fields"]
    assert abs(float(body["results"][0]["lat"]) - 37.5172) < 0.2
    assert abs(float(body["results"][0]["lng"]) - 127.0473) < 0.2


def test_ask_api_uses_yongsan_station_location_alias() -> None:
    response = TestClient(app).post(
        "/api/search/ask?limit=3",
        json={"message": "용산역 가까운 충전소는"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["mode"] == "location"
    assert body["count"] == 3
    assert [result["station_id"] for result in body["results"]] == ["ST-0622", "ST-0504", "ST-0194"]
    assert all("location" in result["matched_fields"] for result in body["results"])


def test_ask_api_rejects_empty_message() -> None:
    response = TestClient(app).post("/api/search/ask", json={"message": ""})

    assert response.status_code == 422
