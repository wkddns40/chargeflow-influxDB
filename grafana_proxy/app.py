from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse

from .security import validate_ds_query_payload


UPSTREAM_URL = os.getenv("GRAFANA_UPSTREAM_URL", "http://grafana:3000").rstrip("/")
TIMEOUT = httpx.Timeout(30.0, connect=10.0)
PUBLIC_ENTRYPOINT = "/d/station-24h/station-24h?orgId=1&var-station_id=ST-0224&from=now-24h&to=now&kiosk"

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}

BLOCKED_PREFIXES = (
    "/api/admin",
    "/api/datasources",
    "/api/login",
    "/api/org",
    "/api/serviceaccounts",
    "/api/teams",
    "/api/user",
    "/api/users",
    "/explore",
    "/profile",
)

ALLOWED_GET_PREFIXES = (
    "/apis/dashboard.grafana.app/",
    "/api/folders/",
    "/api/plugins/",
    "/api/prometheus/grafana/api/v1/rules",
    "/d/",
    "/d-solo/",
    "/public/",
    "/public-dashboards/",
)

ALLOWED_GET_PATHS = {
    "/",
    "/api/annotations",
    "/api/dashboards/uid/station-24h",
    "/api/frontend/settings",
    "/favicon.ico",
    "/robots.txt",
}

app = FastAPI(title="chargeflow Grafana allowlist proxy", version="0.1.0")


@app.get("/proxy-healthz")
def proxy_healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def proxy(path: str, request: Request) -> Response:
    proxied_path = "/" + path
    if request.method.upper() in {"GET", "HEAD"} and proxied_path in {"/", "/login"}:
        return RedirectResponse(PUBLIC_ENTRYPOINT)

    body = await request.body()
    method = request.method.upper()
    allowed, reason = _is_allowed_request(method, proxied_path, body)
    if not allowed:
        return _forbidden(reason)

    upstream_response = await _forward_request(method, proxied_path, request, body)
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=_response_headers(upstream_response),
        media_type=upstream_response.headers.get("content-type"),
    )


def _is_allowed_request(method: str, path: str, body: bytes) -> tuple[bool, str]:
    if method == "OPTIONS":
        return True, ""
    if method in {"GET", "HEAD"} and path == "/api/login/ping":
        return True, ""
    if any(path.startswith(prefix) for prefix in BLOCKED_PREFIXES):
        return False, "blocked_path"
    if path == "/api/ds/query":
        if method != "POST":
            return False, "method_not_allowed"
        result = validate_ds_query_payload(body)
        return result.allowed, result.reason
    if method not in {"GET", "HEAD"}:
        return False, "method_not_allowed"
    if path in ALLOWED_GET_PATHS:
        return True, ""
    if any(path.startswith(prefix) for prefix in ALLOWED_GET_PREFIXES):
        return True, ""
    return False, "path_not_allowed"


async def _forward_request(method: str, path: str, request: Request, body: bytes) -> httpx.Response:
    query = request.url.query
    upstream = f"{UPSTREAM_URL}{path}"
    if query:
        upstream = f"{upstream}?{query}"

    headers = _request_headers(request)
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False) as client:
        return await client.request(method, upstream, content=body, headers=headers)


def _request_headers(request: Request) -> dict[str, str]:
    headers: dict[str, str] = {}
    for key, value in request.headers.items():
        lower = key.lower()
        if lower in HOP_BY_HOP_HEADERS or lower in {"host", "cookie", "authorization"}:
            continue
        headers[key] = value
    return headers


def _response_headers(response: httpx.Response) -> dict[str, str]:
    headers: dict[str, str] = {}
    for key, value in response.headers.items():
        lower = key.lower()
        if lower in HOP_BY_HOP_HEADERS or lower in {"content-encoding", "content-length", "set-cookie"}:
            continue
        headers[key] = value
    return headers


def _forbidden(reason: str) -> JSONResponse:
    return JSONResponse({"message": "forbidden", "reason": reason}, status_code=403)
