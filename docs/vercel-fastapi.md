# Vercel FastAPI

이 문서는 `chargeflow-influxDB` backend를 Vercel Hobby에 올리는 기준입니다.
Vercel API는 station metadata와 Grafana iframe URL만 제공합니다.
InfluxDB는 Vercel에서 직접 query하지 않습니다.

## Entry

Vercel은 repo root를 project root로 사용합니다.

```text
server.py
  -> backend/app/main.py
  -> FastAPI app
```

Root `requirements.txt`는 `backend/requirements.txt`를 참조합니다.
`vercel.json`은 모든 route를 `server.py`로 rewrite합니다.

## Runtime Metadata

Vercel runtime에서 읽는 station metadata는 repo에 포함된 파일을 사용합니다.

```text
backend/data/generated/stations_seoul-gyeonggi.json
```

기본 backend data dir:

```text
backend/data/generated
```

필요하면 Vercel env에서 명시합니다.

```env
APP_ENV=vercel
CHARGER_DATA_DIR=backend/data/generated
GRAFANA_BASE_URL=https://grafana.woonjang.dev
```

`INFLUXDB_URL`은 Vercel runtime에 설정하지 않습니다.
InfluxDB는 local Docker network 내부에서 Grafana만 접근합니다.

## Required API

```text
GET /healthz
GET /api/stations?profile=seoul-gyeonggi&limit=700
GET /api/stations/ST-0001
GET /api/grafana/station-timeline-url?station_id=ST-0001
```

`POST /api/search/ask`는 다음 단계에서 추가합니다.

## Verify

Local:

```powershell
python -m pytest backend/tests
python -c "from server import app; print(app.title)"
```

After Vercel deploy:

```powershell
curl https://<vercel-fastapi-origin>/healthz
curl "https://<vercel-fastapi-origin>/api/stations?profile=seoul-gyeonggi&limit=700"
curl "https://<vercel-fastapi-origin>/api/grafana/station-timeline-url?station_id=ST-0001"
```

Expected:

- `/healthz` returns `{"status":"ok","env":"vercel"}` when `APP_ENV=vercel`.
- station list returns 700 rows for `seoul-gyeonggi`.
- Grafana URL starts with `https://grafana.woonjang.dev`.
- Backend response does not depend on direct InfluxDB access.
