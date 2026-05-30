from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class InfluxWriteResult:
    file: str
    bytes_written: int
    status_code: int


def write_line_protocol_file(
    *,
    url: str,
    database: str,
    path: Path,
    token: str | None = None,
    chunk_size: int = 5000,
) -> list[InfluxWriteResult]:
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    if not path.exists():
        raise FileNotFoundError(path)

    endpoint = f"{url.rstrip('/')}/api/v3/write_lp?{urlencode({'db': database, 'precision': 'nanosecond'})}"
    results: list[InfluxWriteResult] = []
    batch: list[str] = []

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                batch.append(line)
            if len(batch) >= chunk_size:
                results.append(_post_batch(endpoint, batch, token, path))
                batch = []

    if batch:
        results.append(_post_batch(endpoint, batch, token, path))

    return results


def _post_batch(
    endpoint: str,
    batch: list[str],
    token: str | None,
    path: Path,
) -> InfluxWriteResult:
    payload = "".join(batch).encode("utf-8")
    headers = {"Content-Type": "text/plain"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(endpoint, data=payload, headers=headers, method="POST")
    with urlopen(request, timeout=30) as response:
        return InfluxWriteResult(
            file=str(path),
            bytes_written=len(payload),
            status_code=response.status,
        )
