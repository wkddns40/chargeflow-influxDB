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

SEOUL_GYEONGGI_REGION_CENTERS = [
    ("Seoul", 37.5665, 126.9780),
    ("Incheon", 37.4563, 126.7052),
    ("Gyeonggi", 37.2636, 127.0286),
    ("Gyeonggi", 37.4202, 127.1265),
    ("Gyeonggi", 37.6584, 126.8320),
    ("Gyeonggi", 37.2411, 127.1776),
    ("Gyeonggi", 37.7599, 126.7800),
    ("Gyeonggi", 37.7381, 127.0338),
    ("Gyeonggi", 37.6360, 127.2165),
    ("Gyeonggi", 37.3219, 126.8309),
    ("Gyeonggi", 37.1995, 126.8312),
    ("Gyeonggi", 37.2723, 127.4350),
]

REGION_CENTERS_BY_PROFILE = {
    "seoul-gyeonggi": SEOUL_GYEONGGI_REGION_CENTERS,
}

OPERATORS = ["ChargeFlow", "K-Energy", "EVLine", "GridPlug"]
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


def generate_stations(profile: str, seed: int) -> list[dict[str, object]]:
    config = profile_config(profile)
    region_centers = REGION_CENTERS_BY_PROFILE.get(profile, REGION_CENTERS)
    rng = random.Random(seed)
    stations: list[dict[str, object]] = []

    for index in range(1, config["stations"] + 1):
        region, lat, lng = rng.choice(region_centers)
        station_id = f"ST-{index:04d}"
        stations.append(
            {
                "station_id": station_id,
                "name": f"Charge Node {index:04d}",
                "address": f"{region} local road {index:04d}",
                "region": region,
                "operator": rng.choice(OPERATORS),
                "lat": round(lat + rng.uniform(-0.18, 0.18), 6),
                "lng": round(lng + rng.uniform(-0.18, 0.18), 6),
                "connector_count": rng.choice([2, 4, 6]),
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
