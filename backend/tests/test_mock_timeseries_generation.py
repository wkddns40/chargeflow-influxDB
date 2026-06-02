from pathlib import Path

from tools.mockgen import CONNECTOR_COUNT, generate_stations, generate_timeseries, parse_end, profile_config


def test_generate_timeseries_files(tmp_path: Path) -> None:
    stations = generate_stations("smoke", seed=42)[:1]
    paths = generate_timeseries(
        stations,
        profile="smoke",
        seed=42,
        output_dir=tmp_path,
        end=parse_end("2026-01-01T00:00:00Z"),
    )

    assert {path.name for path in paths} == {
        "connector_status_smoke.lp",
        "charger_power_smoke.lp",
        "availability_rollup_smoke.lp",
    }
    assert "connector_status,station_id=ST-0001" in (tmp_path / "connector_status_smoke.lp").read_text(
        encoding="utf-8"
    )


def test_generate_seoul_gyeonggi_timeseries_files(tmp_path: Path) -> None:
    stations = generate_stations("seoul-gyeonggi", seed=42)[:1]
    paths = generate_timeseries(
        stations,
        profile="seoul-gyeonggi",
        seed=42,
        output_dir=tmp_path,
        end=parse_end("2026-01-01T00:00:00Z"),
    )

    assert {path.name for path in paths} == {
        "connector_status_seoul-gyeonggi.lp",
        "charger_power_seoul-gyeonggi.lp",
        "availability_rollup_seoul-gyeonggi.lp",
    }
    assert "connector_status,station_id=ST-0001" in (
        tmp_path / "connector_status_seoul-gyeonggi.lp"
    ).read_text(encoding="utf-8")


def test_seoul_gyeonggi_profile_uses_ten_minute_timeseries() -> None:
    config = profile_config("seoul-gyeonggi")

    assert config["stations"] == 700
    assert config["hours"] == 24 * 7
    assert config["step_minutes"] == 10


def test_generated_stations_use_fixed_connector_count() -> None:
    stations = generate_stations("seoul-gyeonggi", seed=42)

    assert {station["connector_count"] for station in stations} == {CONNECTOR_COUNT}
