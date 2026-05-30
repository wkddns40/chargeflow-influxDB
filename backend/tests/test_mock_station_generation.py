from pathlib import Path

from tools.mockgen import generate_stations, write_stations

SEOUL_GYEONGGI_BBOX = {
    "west": 126.45,
    "south": 36.85,
    "east": 127.85,
    "north": 38.35,
}


def test_generate_smoke_station_count() -> None:
    stations = generate_stations("smoke", seed=42)

    assert len(stations) == 300
    assert stations[0]["station_id"] == "ST-0001"
    assert 33.0 <= float(stations[0]["lat"]) <= 38.8


def test_generate_seoul_gyeonggi_station_count_and_bounds() -> None:
    stations = generate_stations("seoul-gyeonggi", seed=42)

    assert len(stations) == 700
    assert stations[0]["station_id"] == "ST-0001"
    assert stations[-1]["station_id"] == "ST-0700"
    assert {str(station["region"]) for station in stations} <= {"Seoul", "Gyeonggi", "Incheon"}

    for station in stations:
        lat = float(station["lat"])
        lng = float(station["lng"])
        assert SEOUL_GYEONGGI_BBOX["south"] <= lat <= SEOUL_GYEONGGI_BBOX["north"]
        assert SEOUL_GYEONGGI_BBOX["west"] <= lng <= SEOUL_GYEONGGI_BBOX["east"]


def test_write_stations_json(tmp_path: Path) -> None:
    stations = generate_stations("smoke", seed=42)[:2]
    path = write_stations(stations, "smoke", tmp_path)

    assert path.name == "stations_smoke.json"
    assert path.read_text(encoding="utf-8").startswith("[")
