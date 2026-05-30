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
