from pathlib import Path

import pytest

from backend.app.influx.client import write_line_protocol_file
from tools.seed_influx import build_parser


def test_seed_rejects_invalid_chunk_size(tmp_path: Path) -> None:
    lp = tmp_path / "sample.lp"
    lp.write_text("charger_power,station_id=ST-0001 power_kw=1.0 1\n", encoding="utf-8")

    with pytest.raises(ValueError):
        write_line_protocol_file(url="http://localhost:8181", database="charger", path=lp, chunk_size=0)


def test_seed_accepts_seoul_gyeonggi_profile() -> None:
    args = build_parser().parse_args(["--profile", "seoul-gyeonggi"])

    assert args.profile == "seoul-gyeonggi"
