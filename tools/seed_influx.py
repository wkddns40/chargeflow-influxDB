from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
TOOLS = ROOT / "tools"
for path in (ROOT, BACKEND, TOOLS):
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

from app.influx.client import write_line_protocol_file  # noqa: E402
from mockgen import generate_all, parse_end  # noqa: E402


def lp_files(data_dir: Path, profile: str) -> list[Path]:
    return [
        data_dir / f"connector_status_{profile}.lp",
        data_dir / f"charger_power_{profile}.lp",
        data_dir / f"availability_rollup_{profile}.lp",
    ]


def ensure_mock_data(data_dir: Path, profile: str, seed: int) -> None:
    required = [data_dir / f"stations_{profile}.json", *lp_files(data_dir, profile)]
    if all(path.exists() for path in required):
        return
    generate_all(profile=profile, seed=seed, output_dir=data_dir, end=parse_end(None))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Seed local InfluxDB 3 Core with mock line protocol.")
    parser.add_argument("--profile", default="smoke", choices=["smoke", "seoul-gyeonggi", "dev", "perf"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--data-dir", type=Path, default=Path("data/generated"))
    parser.add_argument("--url", default=os.getenv("INFLUXDB_URL", "http://localhost:8181"))
    parser.add_argument("--database", default=os.getenv("INFLUXDB_DATABASE", "charger"))
    parser.add_argument("--token", default=os.getenv("INFLUXDB_TOKEN"))
    parser.add_argument("--chunk-size", type=int, default=5000)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ensure_mock_data(args.data_dir, args.profile, args.seed)

    results = []
    for path in lp_files(args.data_dir, args.profile):
        results.extend(
            write_line_protocol_file(
                url=args.url,
                database=args.database,
                path=path,
                token=args.token,
                chunk_size=args.chunk_size,
            )
        )
    print(json.dumps([result.__dict__ for result in results], indent=2))


if __name__ == "__main__":
    main()
