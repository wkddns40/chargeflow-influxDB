from fastapi.testclient import TestClient

from app.main import app


def test_grafana_url_includes_station_variable() -> None:
    response = TestClient(app).get("/api/grafana/station-timeline-url?station_id=ST-0001")
    assert response.status_code == 200
    body = response.json()
    assert body["station_id"] == "ST-0001"
    assert "var-station_id=ST-0001" in body["url"]
    assert "from=now-24h" in body["url"]
