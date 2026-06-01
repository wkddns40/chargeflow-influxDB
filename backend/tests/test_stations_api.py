import json

from fastapi.testclient import TestClient

from app.main import app
from app.api import stations


def test_station_api_reads_generated_metadata(tmp_path, monkeypatch) -> None:
    generated = tmp_path / "stations_smoke.json"
    generated.write_text(
        json.dumps(
            [
                {
                    "station_id": "ST-0001",
                    "name": "Station 1",
                    "address": "Seoul",
                    "region": "Seoul",
                    "operator": "Mock",
                    "lat": 37.56,
                    "lng": 126.98,
                    "connector_count": 4,
                }
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(stations, "_station_file", lambda profile: generated)

    response = TestClient(app).get("/api/stations")

    assert response.status_code == 200
    assert response.json()["stations"][0]["station_id"] == "ST-0001"


def test_station_api_reads_seoul_gyeonggi_deploy_metadata() -> None:
    response = TestClient(app).get("/api/stations?profile=seoul-gyeonggi&limit=700")

    body = response.json()
    assert response.status_code == 200
    assert body["profile"] == "seoul-gyeonggi"
    assert body["count"] == 700
    assert body["stations"][0]["station_id"] == "ST-0001"
    assert body["stations"][-1]["station_id"] == "ST-0700"


def test_station_detail_defaults_to_seoul_gyeonggi_metadata() -> None:
    response = TestClient(app).get("/api/stations/ST-0001")

    assert response.status_code == 200
    assert response.json()["station_id"] == "ST-0001"


def test_station_profile_validation_rejects_unknown_profile() -> None:
    response = TestClient(app).get("/api/stations?profile=unknown")

    assert response.status_code == 422
