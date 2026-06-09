# chargeflow-influxDB

`chargeflow-influxDB`는 ChargeFlow EV 충전소 지도에서 선택한 충전소의 InfluxDB 시계열 데이터를 Grafana iframe으로 보여주는 `deployed demo for InfluxDB + Grafana timeline`입니다.

## 데모 URL

- Demo site: [chargeflow-influxdb.pages.dev](https://chargeflow-influxdb.pages.dev)
- API health: [chargeflow-influxdb.vercel.app/healthz](https://chargeflow-influxdb.vercel.app/healthz)
- Station API: `https://chargeflow-influxdb.vercel.app/api/stations?profile=seoul-gyeonggi&limit=700`
- Ask API: `https://chargeflow-influxdb.vercel.app/api/search/ask`
- Grafana URL API: `https://chargeflow-influxdb.vercel.app/api/grafana/station-timeline-url?station_id=ST-0224`
- Grafana dashboard: [grafana.woonjang.dev](https://grafana.woonjang.dev/d/station-24h/station-24h?orgId=1&var-station_id=ST-0224&from=now-24h&to=now&kiosk)

이 README의 기준은 로컬 런타임 검증이 아니라 **배포된 데모 검증**입니다. Cloudflare Pages가 Vercel FastAPI를 호출하고, Grafana iframe은 AWS EC2에서 실행되는 Cloudflare Tunnel origin으로 연결됩니다.

## AWS 배포 구조

```text
Cloudflare Pages React app
  -> Vercel FastAPI station/search/Grafana URL APIs
  -> Cloudflare Tunnel HTTPS origin
  -> AWS EC2 Docker Compose
  -> grafana-proxy allowlist
  -> Grafana OSS station dashboard
  -> InfluxDB 3 Core mock time-series data
```

| 항목 | 기준 |
|---|---|
| Compute | AWS EC2 `m7i-flex.large` |
| OS | Ubuntu |
| App path | `/opt/chargeflow-influxdb` |
| Runtime | Docker Compose |
| Restart policy | `restart: unless-stopped` |
| Public Grafana origin | AWS `cloudflared` container |
| Public hostname | `grafana.woonjang.dev` |
| App bind address | service ports are bound to `127.0.0.1` |
| External access | Cloudflare Tunnel outbound connector only |
| InfluxDB image | migrated data와 맞는 `influxdb:3-core` digest 고정 |

Vercel FastAPI는 station metadata, Ask 검색, health check, Grafana iframe URL 생성만 담당합니다. 공개 데모 경로에서 Vercel은 InfluxDB를 직접 query하지 않고, Grafana가 AWS Docker network 내부에서 InfluxDB를 query합니다.

```

## 운영 검증

배포 데모 smoke check:

```powershell
curl.exe -I https://chargeflow-influxdb.pages.dev/
curl.exe https://chargeflow-influxdb.vercel.app/healthz
curl.exe "https://chargeflow-influxdb.vercel.app/api/grafana/station-timeline-url?station_id=ST-0224"
curl.exe -I "https://grafana.woonjang.dev/d/station-24h/station-24h?orgId=1&var-station_id=ST-0224&from=now-24h&to=now&kiosk"
```

AWS host check:

```bash
cd /opt/chargeflow-influxdb
sudo docker compose -f docker-compose.yml -f docker-compose.aws.yml ps
sudo docker compose -f docker-compose.yml -f docker-compose.aws.yml logs --tail=80 cloudflared
sudo docker compose exec -T influxdb3-core influxdb3 query --database charger 'SELECT count(*) AS n FROM connector_status'
sudo docker compose exec -T influxdb3-core influxdb3 query --database charger 'SELECT count(*) AS n FROM charger_power'
sudo docker compose exec -T influxdb3-core influxdb3 query --database charger 'SELECT count(*) AS n FROM availability_rollup'
```

현재 seeded data contract:

| Table | Expected count |
|---|---:|
| `connector_status` | `2,118,900` |
| `charger_power` | `2,118,900` |
| `availability_rollup` | `706,300` |

공개 경로 기대 동작:

1. `https://chargeflow-influxdb.pages.dev/`에서 지도 화면이 로드됩니다.
2. 초기 데모 흐름에서 Ask 결과가 표시됩니다.
3. 충전소 선택 시 우측 Grafana iframe이 열립니다.
4. iframe URL에 `var-station_id=<선택 station>`이 포함됩니다.
5. Grafana panel이 no data 없이 표시됩니다.
6. `grafana.woonjang.dev` 전체화면 dashboard가 열립니다.
