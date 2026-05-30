from dataclasses import dataclass
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "local")
    data_dir: Path = _resolve_path(os.getenv("CHARGER_DATA_DIR", "data/generated"))
    grafana_base_url: str = os.getenv("GRAFANA_BASE_URL", "http://localhost:3001")
    influxdb_url: str = os.getenv("INFLUXDB_URL", "http://localhost:8181")
    influxdb_database: str = os.getenv("INFLUXDB_DATABASE", "charger")


def get_settings() -> Settings:
    return Settings()
