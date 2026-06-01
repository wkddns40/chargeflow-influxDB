# End-to-end deployment verification

이 문서는 `chargeflow-influxDB`의 무료 로컬 자가호스팅 데모가 계획서 기준으로 연결되는지 확인하는 절차입니다.

## 대상 구성

- Cloudflare Pages frontend
- Vercel FastAPI backend
- Local Grafana OSS
- Local InfluxDB 3 Core
- Cloudflare Tunnel for Grafana HTTPS

## 필수 환경값

```text
VITE_API_BASE_URL=https://chargeflow-influxdb.vercel.app
GRAFANA_BASE_URL=https://grafana.woonjang.dev
GRAFANA_ROOT_URL=https://grafana.woonjang.dev
```

## 검증 순서

1. Vercel FastAPI health

```powershell
Invoke-RestMethod https://chargeflow-influxdb.vercel.app/healthz
```

기대값:

```text
status = ok
```

2. station metadata 700개 반환

```powershell
Invoke-RestMethod "https://chargeflow-influxdb.vercel.app/api/stations?profile=seoul-gyeonggi&limit=700"
```

기대값:

```text
count = 700
```

3. Grafana tunnel URL 생성

```powershell
Invoke-RestMethod "https://chargeflow-influxdb.vercel.app/api/grafana/station-timeline-url?station_id=ST-0001"
```

기대값:

```text
url contains https://grafana.woonjang.dev
url contains var-station_id=ST-0001
```

4. Grafana local dashboard data

```powershell
Invoke-WebRequest "https://grafana.woonjang.dev/d/station-24h/station-24h?orgId=1&var-station_id=ST-0001&from=now-24h&to=now&kiosk"
```

기대값:

```text
HTTP 200
iframe 차단 헤더 없음
ST-0001 panel no data 없음
```

5. frontend smoke

```text
Cloudflare Pages frontend 접속
지도 pan/zoom 동작 확인
충전소 마커 클릭
Grafana iframe 로드 확인
fullscreen 진입
panel view 복귀
Ask 검색 후 station focus 확인
```

## 완료 기준

- Cloudflare Pages -> Vercel FastAPI 연결 OK
- Vercel FastAPI -> tunnel Grafana URL 생성 OK
- tunnel Grafana -> local InfluxDB query OK
- 마커 클릭부터 timeline 표시까지 end-to-end OK
- Ask 검색 결과 선택 시 지도 focus와 Grafana timeline 표시 OK
