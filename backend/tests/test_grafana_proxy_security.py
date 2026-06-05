import json

from fastapi.testclient import TestClient

from grafana_proxy.app import _is_allowed_request
from grafana_proxy.app import app as grafana_proxy_app
from grafana_proxy.security import validate_ds_query_payload


def _payload(sql: str, uid: str = "influxdb-charger-mock") -> bytes:
    return json.dumps(
        {
            "queries": [
                {
                    "datasource": {"type": "influxdb", "uid": uid},
                    "rawQuery": True,
                    "rawSql": sql,
                    "query": sql,
                    "refId": "A",
                }
            ],
            "from": "now-24h",
            "to": "now",
        }
    ).encode()


def _timeline_sql(table: str, field_sql: str) -> str:
    return (
        f"WITH latest AS (SELECT max(time) AS latest_time FROM {table} "
        "WHERE station_id = 'ST-0224') "
        "SELECT time + (now() - (SELECT latest_time FROM latest)) AS time, "
        f"{field_sql} FROM {table} WHERE station_id = 'ST-0224' "
        "AND time >= (SELECT latest_time FROM latest) - INTERVAL '24 hours' "
        "AND time <= (SELECT latest_time FROM latest) ORDER BY time"
    )


def test_allows_dashboard_panel_queries() -> None:
    queries = [
        _timeline_sql("connector_status", "connector_id, status_code"),
        _timeline_sql("charger_power", "connector_id, power_kw"),
        _timeline_sql("availability_rollup", "available"),
        _timeline_sql("availability_rollup", "ratio * 100 AS availability_pct"),
    ]

    for sql in queries:
        assert validate_ds_query_payload(_payload(sql)).allowed


def test_blocks_schema_and_station_list_queries() -> None:
    schema = "SELECT table_name, column_name FROM information_schema.columns"
    station_list = "SELECT DISTINCT station_id FROM connector_status ORDER BY station_id LIMIT 700"

    assert not validate_ds_query_payload(_payload(schema)).allowed
    assert not validate_ds_query_payload(_payload(station_list)).allowed


def test_blocks_bad_datasource_and_station_id() -> None:
    sql = _timeline_sql("connector_status", "connector_id, status_code")
    bad_station = sql.replace("ST-0224", "admin")

    assert not validate_ds_query_payload(_payload(sql, uid="other")).allowed
    assert not validate_ds_query_payload(_payload(bad_station)).allowed


def test_blocks_datasource_api_paths() -> None:
    assert _is_allowed_request("GET", "/api/datasources", b"") == (False, "blocked_path")
    assert _is_allowed_request("GET", "/api/datasources/uid/influxdb-charger-mock", b"") == (
        False,
        "blocked_path",
    )


def test_allows_login_ping_without_opening_login_api() -> None:
    assert _is_allowed_request("GET", "/api/login/ping", b"") == (True, "")
    assert _is_allowed_request("GET", "/api/login", b"") == (False, "blocked_path")


def test_redirects_public_entrypoints_to_dashboard() -> None:
    client = TestClient(grafana_proxy_app)

    for path in ("/", "/login"):
        response = client.get(path, follow_redirects=False)

        assert response.status_code == 307
        assert response.headers["location"].startswith("/d/station-24h/station-24h?")
