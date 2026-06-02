import json
from pathlib import Path


def test_station_dashboard_uses_latest_seeded_window() -> None:
    dashboard = json.loads(Path("grafana/dashboards/station_24h.json").read_text(encoding="utf-8"))
    queries = [
        target["query"]
        for panel in dashboard["panels"]
        for target in panel.get("targets", [])
        if "query" in target
    ]

    assert queries
    for query in queries:
        assert "$__timeFilter" not in query
        assert "max(time) AS latest_time" in query
        assert "time + (now() - (SELECT latest_time FROM latest)) AS time" in query
        assert "INTERVAL '24 hours'" in query
