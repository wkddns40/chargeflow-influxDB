from __future__ import annotations

import argparse
import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Iterable


PROFILES = {
    "smoke": {"stations": 300, "hours": 24, "step_minutes": 15},
    "seoul-gyeonggi": {"stations": 700, "hours": 24 * 7, "step_minutes": 60},
    "dev": {"stations": 7000, "hours": 24 * 7, "step_minutes": 60},
    "perf": {"stations": 7000, "hours": 24 * 30, "step_minutes": 60},
}

REGION_CENTERS = [
    ("Seoul", 37.5665, 126.9780),
    ("Incheon", 37.4563, 126.7052),
    ("Daejeon", 36.3504, 127.3845),
    ("Daegu", 35.8714, 128.6014),
    ("Gwangju", 35.1595, 126.8526),
    ("Busan", 35.1796, 129.0756),
    ("Jeju", 33.4996, 126.5312),
]

SEOUL_GYEONGGI_STATION_AREAS = [
    ("Seoul", "Gangnam", 37.4990, 37.5170, 127.0340, 127.0620),
    ("Seoul", "Seocho", 37.4780, 37.5000, 127.0020, 127.0260),
    ("Seoul", "Jamsil", 37.5000, 37.5150, 127.0950, 127.1200),
    ("Seoul", "Mapo", 37.5520, 37.5680, 126.9000, 126.9250),
    ("Seoul", "Seongdong", 37.5450, 37.5650, 127.0300, 127.0550),
    ("Seoul", "Yongsan", 37.5320, 37.5420, 126.9680, 126.9950),
    ("Seoul", "Jongno", 37.5680, 37.5880, 126.9700, 126.9950),
    ("Seoul", "Guro", 37.4880, 37.5060, 126.8740, 126.9040),
    ("Seoul", "Nowon", 37.6420, 37.6700, 127.0450, 127.0750),
    ("Incheon", "Bupyeong", 37.4880, 37.5200, 126.7000, 126.7350),
    ("Incheon", "Songdo", 37.3600, 37.4050, 126.6250, 126.6900),
    ("Incheon", "Cheongna", 37.5200, 37.5450, 126.6200, 126.6750),
    ("Gyeonggi", "Suwon", 37.2550, 37.2850, 127.0150, 127.0450),
    ("Gyeonggi", "Seongnam", 37.4050, 37.4350, 127.1250, 127.1580),
    ("Gyeonggi", "Yongin", 37.2300, 37.2600, 127.1150, 127.1500),
    ("Gyeonggi", "Goyang", 37.6380, 37.6680, 126.7750, 126.8150),
    ("Gyeonggi", "Bucheon", 37.4880, 37.5120, 126.7550, 126.7820),
    ("Gyeonggi", "Ansan", 37.3050, 37.3350, 126.8200, 126.8520),
    ("Gyeonggi", "Anyang", 37.3850, 37.4050, 126.9480, 126.9700),
    ("Gyeonggi", "Uijeongbu", 37.7280, 37.7550, 127.0250, 127.0550),
    ("Gyeonggi", "Namyangju", 37.6250, 37.6520, 127.1950, 127.2300),
    ("Gyeonggi", "Hanam", 37.5320, 37.5520, 127.1900, 127.2350),
    ("Gyeonggi", "Gimpo", 37.6050, 37.6280, 126.7000, 126.7350),
    ("Gyeonggi", "Gwangmyeong", 37.4680, 37.4900, 126.8500, 126.8750),
    ("Gyeonggi", "Siheung", 37.3700, 37.3950, 126.7850, 126.8200),
]

STATION_EXCLUSION_ZONES = [
    (37.5200, 37.5500, 126.8750, 126.9550),
    (37.5150, 37.5300, 126.9550, 127.0200),
    (37.5150, 37.5450, 127.0200, 127.1000),
    (37.5150, 37.5350, 127.1000, 127.1800),
]

OPERATORS = ["ChargeFlow", "K-Energy", "EVLine", "GridPlug"]
MAX_KW_VALUES = [7, 11, 22, 50, 100, 150, 200, 350]
STATUS = {"available": 1, "charging": 2, "faulted": 3, "offline": 4}


def parse_end(value: str | None) -> datetime:
    if not value:
        now = datetime.now(UTC)
        return now.replace(second=0, microsecond=0)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def profile_config(profile: str) -> dict[str, int]:
    try:
        return PROFILES[profile]
    except KeyError as exc:
        raise ValueError(f"unknown profile: {profile}") from exc


def is_excluded_station_point(lat: float, lng: float) -> bool:
    return any(
        lat_min <= lat <= lat_max and lng_min <= lng <= lng_max
        for lat_min, lat_max, lng_min, lng_max in STATION_EXCLUSION_ZONES
    )


def seoul_gyeonggi_point(area: tuple[str, str, float, float, float, float], rng: random.Random) -> tuple[float, float]:
    _, _, lat_min, lat_max, lng_min, lng_max = area
    for _ in range(50):
        lat = rng.uniform(lat_min, lat_max)
        lng = rng.uniform(lng_min, lng_max)
        if not is_excluded_station_point(lat, lng):
            return lat, lng
    return (lat_min + lat_max) / 2, (lng_min + lng_max) / 2


def generate_stations(profile: str, seed: int) -> list[dict[str, object]]:
    config = profile_config(profile)
    rng = random.Random(seed)
    stations: list[dict[str, object]] = []

    for index in range(1, config["stations"] + 1):
        if profile == "seoul-gyeonggi":
            selected_area = rng.choice(SEOUL_GYEONGGI_STATION_AREAS)
            region, area, *_ = selected_area
            lat, lng = seoul_gyeonggi_point(selected_area, rng)
        else:
            region, lat, lng = rng.choice(REGION_CENTERS)
            area = region
            lat = lat + rng.uniform(-0.18, 0.18)
            lng = lng + rng.uniform(-0.18, 0.18)
        station_id = f"ST-{index:04d}"
        connector_count = rng.choice([2, 4, 6])
        stations.append(
            {
                "station_id": station_id,
                "name": f"Charge Node {index:04d}",
                "address": f"{area} local road {index:04d}",
                "region": region,
                "operator": rng.choice(OPERATORS),
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "connector_count": connector_count,
                "max_kw": rng.choice(MAX_KW_VALUES),
            }
        )

    return stations


def write_stations(stations: list[dict[str, object]], profile: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"stations_{profile}.json"
    path.write_text(json.dumps(stations, indent=2, ensure_ascii=True), encoding="utf-8")
    return path


def generate_timeseries(
    stations: list[dict[str, object]],
    *,
    profile: str,
    seed: int,
    output_dir: Path,
    end: datetime,
) -> list[Path]:
    config = profile_config(profile)
    output_dir.mkdir(parents=True, exist_ok=True)

    status_path = output_dir / f"connector_status_{profile}.lp"
    power_path = output_dir / f"charger_power_{profile}.lp"
    rollup_path = output_dir / f"availability_rollup_{profile}.lp"

    start = end - timedelta(hours=config["hours"])
    step = timedelta(minutes=config["step_minutes"])
    points = int((end - start) / step) + 1

    with (
        status_path.open("w", encoding="utf-8", newline="\n") as status_file,
        power_path.open("w", encoding="utf-8", newline="\n") as power_file,
        rollup_path.open("w", encoding="utf-8", newline="\n") as rollup_file,
    ):
        for station in stations:
            station_id = str(station["station_id"])
            connector_count = int(station["connector_count"])
            for point in range(points):
                timestamp = int((start + step * point).timestamp() * 1_000_000_000)
                available = 0
                for connector_id in range(1, connector_count + 1):
                    state, power_kw = connector_state(seed, station_id, connector_id, point)
                    if state == "available":
                        available += 1
                    status_file.write(
                        "connector_status,"
                        f"station_id={station_id},connector_id={connector_id} "
                        f"status_code={STATUS[state]}i {timestamp}\n"
                    )
                    power_file.write(
                        "charger_power,"
                        f"station_id={station_id},connector_id={connector_id} "
                        f"power_kw={power_kw:.2f} {timestamp}\n"
                    )
                ratio = available / connector_count
                rollup_file.write(
                    "availability_rollup,"
                    f"station_id={station_id} "
                    f"available={available}i,total={connector_count}i,ratio={ratio:.4f} {timestamp}\n"
                )

    return [status_path, power_path, rollup_path]


def connector_state(seed: int, station_id: str, connector_id: int, point: int) -> tuple[str, float]:
    rng = random.Random(f"{seed}:{station_id}:{connector_id}:{point}")
    value = rng.random()
    if value < 0.58:
        return "available", 0.0
    if value < 0.88:
        return "charging", rng.uniform(7.0, 150.0)
    if value < 0.96:
        return "faulted", 0.0
    return "offline", 0.0


def generate_all(profile: str, seed: int, output_dir: Path, end: datetime) -> list[Path]:
    stations = generate_stations(profile, seed)
    station_path = write_stations(stations, profile, output_dir)
    return [station_path, *generate_timeseries(stations, profile=profile, seed=seed, output_dir=output_dir, end=end)]


def print_paths(paths: Iterable[Path]) -> None:
    for path in paths:
        print(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate local EV charger mock data.")
    parser.add_argument("target", choices=["stations", "all"])
    parser.add_argument("--profile", default="smoke", choices=sorted(PROFILES))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("data/generated"))
    parser.add_argument("--end", help="UTC end timestamp, for example 2026-01-01T00:00:00Z")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    end = parse_end(args.end)
    stations = generate_stations(args.profile, args.seed)
    paths = [write_stations(stations, args.profile, args.output_dir)]
    if args.target == "all":
        paths.extend(
            generate_timeseries(
                stations,
                profile=args.profile,
                seed=args.seed,
                output_dir=args.output_dir,
                end=end,
            )
        )
    print_paths(paths)


if __name__ == "__main__":
    main()
