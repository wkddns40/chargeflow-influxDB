from fastapi.testclient import TestClient

from app.main import app


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


def test_ask_api_rejects_empty_message() -> None:
    response = TestClient(app).post("/api/search/ask", json={"message": ""})

    assert response.status_code == 422
