# Local Development

## Setup

```powershell
Copy-Item .env.example .env
.\scripts\setup-local.ps1
```

## Run

```powershell
docker compose up -d
```

All published ports bind to `127.0.0.1` by default. This keeps InfluxDB and Grafana reachable from the local host while avoiding LAN exposure. Change `LOCAL_BIND_ADDRESS` in `.env` only when you intentionally need another bind address.

For local backend work:

```powershell
python -m pip install -r backend\requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

For frontend work:

```powershell
cd frontend
npm install
npm run dev
```

## Seed InfluxDB

Smoke profile:

```powershell
.\scripts\seed-smoke.ps1
```

Free local demo profile:

```powershell
.\scripts\seed-smoke.ps1 -Profile seoul-gyeonggi
```

Direct seed command:

```powershell
python tools\seed_influx.py --profile seoul-gyeonggi --seed 42
```

## Verify

```powershell
.\scripts\verify-local.ps1
```

## Grafana Root URL

Local iframe testing uses:

```text
GRAFANA_ROOT_URL=http://localhost:3001
GRAFANA_BASE_URL=http://localhost:3001
```

When using Cloudflare Tunnel later, set both values to the public tunnel URL before recreating Grafana and backend.
