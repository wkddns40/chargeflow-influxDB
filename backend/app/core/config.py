from dataclasses import dataclass, field
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_DIR = "backend/data/generated"


def _resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


@dataclass(frozen=True)
class Settings:
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "local"))
    data_dir: Path = field(
        default_factory=lambda: _resolve_path(os.getenv("CHARGER_DATA_DIR", DEFAULT_DATA_DIR))
    )
    grafana_base_url: str = field(
        default_factory=lambda: os.getenv("GRAFANA_BASE_URL", "http://localhost:3001")
    )
    influxdb_url: str = field(default_factory=lambda: os.getenv("INFLUXDB_URL", "http://localhost:8181"))
    influxdb_database: str = field(default_factory=lambda: os.getenv("INFLUXDB_DATABASE", "charger"))


def get_settings() -> Settings:
    return Settings()
