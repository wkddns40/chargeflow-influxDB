# Architecture

`chargeflow-influxDB` is a local-only demo package.

## Components

- React/Vite frontend on port `3000`
- FastAPI backend on port `8000`
- Grafana OSS on port `3001`
- InfluxDB 3 Core on port `8181`
- Python mock generator and seed command under `tools/`
- Optional Cloudflare Tunnel for public HTTPS access to Grafana only

Docker Compose binds published ports to `127.0.0.1` by default through `LOCAL_BIND_ADDRESS`. Grafana reaches InfluxDB through the internal Compose service URL `http://influxdb3-core:8181`.
When Cloudflare Tunnel is used, it should route only the public Grafana hostname to `http://127.0.0.1:3001`. InfluxDB should stay private.

## Data Flow

```text
tools/mockgen.py
  -> data/generated/stations_smoke.json
  -> data/generated/stations_seoul-gyeonggi.json
  -> data/generated/*.lp

tools/seed_influx.py
  -> InfluxDB /api/v3/write_lp

frontend
  -> backend /api/stations
  -> backend /api/grafana/station-timeline-url
  -> Grafana iframe
  -> local Grafana or Cloudflare Tunnel Grafana URL
```

The frontend never receives an InfluxDB token. In this local package InfluxDB runs with `--without-auth` for reproducible development and is bound to localhost by default. Do not expose InfluxDB directly to the public internet.

Cloudflare Tunnel setup is documented in [Cloudflare Tunnel](cloudflare-tunnel.md).

## Runtime Data

Runtime files live under `data/` and are ignored by Git:

- `data/generated/`
- `data/influxdb/`
- `data/influxdb-plugins/`
- `data/grafana/`
