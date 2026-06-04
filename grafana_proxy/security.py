from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


ALLOWED_DATASOURCE_UID = "influxdb-charger-mock"
STATION_ID_PATTERN = re.compile(r"^ST-\d{4,5}$")
STATION_ID_SQL_PATTERN = re.compile(r"station_id\s*=\s*'([^']+)'", re.IGNORECASE)
FROM_TABLE_PATTERN = re.compile(r"\bFROM\s+([a-z_][a-z0-9_]*)\b", re.IGNORECASE)
FORBIDDEN_SQL_PATTERN = re.compile(
    r";|--|/\*|\*/|\b(insert|update|delete|drop|alter|create|truncate|copy|union|attach|detach)\b",
    re.IGNORECASE,
)

ALLOWED_TABLES = {
    "connector_status",
    "charger_power",
    "availability_rollup",
}


@dataclass(frozen=True)
class ValidationResult:
    allowed: bool
    reason: str = ""


def validate_ds_query_payload(payload: bytes, datasource_uid: str = ALLOWED_DATASOURCE_UID) -> ValidationResult:
    try:
        body = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return ValidationResult(False, "invalid_json")

    queries = body.get("queries")
    if not isinstance(queries, list) or not queries:
        return ValidationResult(False, "missing_queries")

    for query in queries:
        result = validate_query(query, datasource_uid)
        if not result.allowed:
            return result
    return ValidationResult(True)


def validate_query(query: Any, datasource_uid: str = ALLOWED_DATASOURCE_UID) -> ValidationResult:
    if not isinstance(query, dict):
        return ValidationResult(False, "query_not_object")

    datasource = query.get("datasource")
    if not isinstance(datasource, dict) or datasource.get("uid") != datasource_uid:
        return ValidationResult(False, "datasource_not_allowed")

    sql = query.get("rawSql") or query.get("query")
    if not isinstance(sql, str) or not sql.strip():
        return ValidationResult(False, "missing_sql")

    return validate_sql(sql)


def validate_sql(sql: str) -> ValidationResult:
    normalized = _normalize_sql(sql)
    lower = normalized.lower()

    if FORBIDDEN_SQL_PATTERN.search(normalized):
        return ValidationResult(False, "forbidden_sql_token")
    if "information_schema" in lower:
        return ValidationResult(False, "schema_query_blocked")
    if "select distinct station_id" in lower:
        return ValidationResult(False, "station_list_query_blocked")
    if "select *" in lower:
        return ValidationResult(False, "wildcard_select_blocked")
    if not lower.startswith("with latest as (select max(time) as latest_time from "):
        return ValidationResult(False, "unexpected_query_shape")
    if "time + (now() - (select latest_time from latest)) as time" not in lower:
        return ValidationResult(False, "missing_time_shift")
    if "interval '24 hours'" not in lower:
        return ValidationResult(False, "missing_window")
    if "order by time" not in lower:
        return ValidationResult(False, "missing_order")

    tables = {table.lower() for table in FROM_TABLE_PATTERN.findall(normalized) if table.lower() != "latest"}
    if len(tables) != 1:
        return ValidationResult(False, "multiple_or_missing_tables")
    table = next(iter(tables))
    if table not in ALLOWED_TABLES:
        return ValidationResult(False, "table_not_allowed")

    if not _has_required_fields(table, lower):
        return ValidationResult(False, "missing_required_fields")

    station_ids = STATION_ID_SQL_PATTERN.findall(normalized)
    if not station_ids:
        return ValidationResult(False, "missing_station_id")
    if len(set(station_ids)) != 1:
        return ValidationResult(False, "mixed_station_id")
    if not STATION_ID_PATTERN.fullmatch(station_ids[0]):
        return ValidationResult(False, "invalid_station_id")

    return ValidationResult(True)


def _normalize_sql(sql: str) -> str:
    return " ".join(sql.strip().split())


def _has_required_fields(table: str, sql: str) -> bool:
    if table == "connector_status":
        return "connector_id" in sql and "status_code" in sql
    if table == "charger_power":
        return "connector_id" in sql and "power_kw" in sql
    if table == "availability_rollup":
        return "available" in sql or "ratio" in sql
    return False
