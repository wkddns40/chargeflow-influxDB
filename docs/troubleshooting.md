# Troubleshooting

## Grafana iframe is blank

Run:

```powershell
docker compose restart grafana
```

Then open:

```text
http://localhost:3001/d/station-24h/station-24h?var-station_id=ST-0001&from=now-24h&to=now
```

If the browser redirects to the wrong host, check:

```text
GRAFANA_ROOT_URL=http://localhost:3001
GRAFANA_BASE_URL=http://localhost:3001
```

For Cloudflare Tunnel, both values must use the public tunnel URL.

If the tunnel URL is used, also confirm that `GF_SECURITY_ALLOW_EMBEDDING=true` and that Grafana was recreated after changing `GRAFANA_ROOT_URL`.

## Cloudflare Tunnel returns 404

Check the ingress hostname and catch-all rule:

```powershell
cloudflared tunnel --config cloudflare\tunnel\config.yml ingress validate
cloudflared tunnel --config cloudflare\tunnel\config.yml ingress rule https://grafana.example.com
```

The hostname must match the public Grafana domain, and the Grafana rule must appear before `http_status:404`.

## Cloudflare Tunnel reaches Grafana but iframe redirects

Use the same public HTTPS URL for both values:

```text
GRAFANA_ROOT_URL=https://grafana.example.com
GRAFANA_BASE_URL=https://grafana.example.com
```

Then recreate Grafana and backend:

```powershell
docker compose up -d --force-recreate grafana backend
```

## No stations on the map

Generate metadata:

```powershell
python tools\mockgen.py all --profile smoke --seed 42
docker compose restart backend
```

For the free local demo profile:

```powershell
python tools\mockgen.py all --profile seoul-gyeonggi --seed 42
docker compose restart backend
```

## Timeline has no points

Seed InfluxDB:

```powershell
.\scripts\seed-smoke.ps1
```

Or seed the 700-station Seoul/Gyeonggi/Incheon profile:

```powershell
.\scripts\seed-smoke.ps1 -Profile seoul-gyeonggi
```

If the dashboard still has no points, verify that the selected station id exists in the profile you seeded.

## Port already in use

Edit `.env` and change one of:

```text
LOCAL_BIND_ADDRESS=127.0.0.1
FRONTEND_PORT=3000
BACKEND_PORT=8000
GRAFANA_PORT=3001
INFLUXDB_PORT=8181
```

Ports are bound to `LOCAL_BIND_ADDRESS` by default. Keep this value at `127.0.0.1` unless you intentionally want to expose a service outside the local host.
