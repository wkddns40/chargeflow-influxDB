# Cloudflare Tunnel

이 문서는 로컬 Docker Grafana만 Cloudflare Tunnel로 HTTPS 노출하는 절차입니다.
InfluxDB는 외부에 직접 공개하지 않고, Grafana가 Docker network 내부 주소로만 접근합니다.

## 목적

```text
https://grafana.example.com
  -> Cloudflare Tunnel
  -> http://127.0.0.1:3001
  -> local Grafana OSS
  -> Docker network
  -> http://influxdb3-core:8181
```

## 사전 조건

- Cloudflare 계정과 Cloudflare에 연결된 도메인
- 로컬 host에 설치된 `cloudflared`
- 실행 중인 Docker Compose Grafana
- 강한 Grafana admin 비밀번호

## 설치 확인

Windows에서는 `winget`으로 설치할 수 있습니다.

```powershell
winget install --id Cloudflare.cloudflared -e --accept-source-agreements --accept-package-agreements
cloudflared --version
cloudflared tunnel --help
```

설치 직후 현재 PowerShell 세션에서 `cloudflared`를 찾지 못하면 새 터미널을 열어 PATH alias를 다시 로드합니다.

## 환경 변수

`.env`에서 Grafana 공개 URL을 tunnel domain과 맞춥니다.

```env
LOCAL_BIND_ADDRESS=127.0.0.1
GRAFANA_ROOT_URL=https://grafana.example.com
GRAFANA_BASE_URL=https://grafana.example.com
```

`GRAFANA_ROOT_URL`은 Grafana container의 `GF_SERVER_ROOT_URL`로 들어갑니다.
`GRAFANA_BASE_URL`은 backend가 iframe URL을 만들 때 사용합니다.
두 값이 다르면 iframe redirect 또는 host mismatch 문제가 날 수 있습니다.

변경 후 Grafana와 backend를 다시 만듭니다.

```powershell
docker compose up -d --force-recreate grafana backend
```

## Tunnel 생성

```powershell
cloudflared tunnel login
cloudflared tunnel create chargeflow-grafana
cloudflared tunnel route dns chargeflow-grafana grafana.example.com
```

`cloudflared tunnel login`은 로컬 사용자 프로필의 `.cloudflared` 아래에 `cert.pem`을 만듭니다.
`cloudflared tunnel create`는 tunnel credential JSON 파일을 만듭니다.
두 파일은 secret이므로 repo에 커밋하지 않습니다.

## Config 작성

샘플을 복사한 뒤 실제 tunnel id, 사용자 경로, hostname만 바꿉니다.

```powershell
Copy-Item cloudflare\tunnel\config.example.yml cloudflare\tunnel\config.yml
```

`cloudflare/tunnel/config.yml` 예시:

```yaml
tunnel: <TUNNEL_ID>
credentials-file: 'C:\Users\<USER>\.cloudflared\<TUNNEL_ID>.json'

ingress:
  - hostname: grafana.example.com
    service: http://127.0.0.1:3001
  - service: http_status:404
```

마지막 `http_status:404` catch-all rule은 의도하지 않은 hostname 노출을 막기 위해 유지합니다.

## 실행

```powershell
docker compose up -d grafana backend
cloudflared tunnel --config cloudflare\tunnel\config.yml run chargeflow-grafana
```

Windows service로 상시 실행하려면 수동 실행 검증 후 관리자 권한 CMD에서 service install을 진행합니다.
Cloudflare 공식 Windows service 문서는 `%USERPROFILE%\.cloudflared\config.yml` 또는 service 계정 경로를 기준으로 설명하므로, service 등록 전 config와 credential 경로를 실제 service 실행 계정에 맞춰야 합니다.

## 검증

```powershell
cloudflared tunnel --help
cloudflared tunnel --config cloudflare\tunnel\config.yml ingress validate
cloudflared tunnel --config cloudflare\tunnel\config.yml ingress rule https://grafana.example.com
docker compose config
```

브라우저 확인:

```text
https://grafana.example.com
https://grafana.example.com/d/station-24h/station-24h?var-station_id=ST-0001&from=now-24h&to=now
```

성공 기준:

- 외부 브라우저에서 Grafana가 열립니다.
- anonymous Viewer로 dashboard 접근이 됩니다.
- iframe에서 X-Frame-Options 또는 CSP 차단이 없습니다.
- Grafana datasource는 `http://influxdb3-core:8181`을 계속 사용합니다.
- InfluxDB `8181` 포트는 외부에 공개하지 않습니다.

## 보안 메모

- `cloudflare/tunnel/config.yml`, `*.json`, `*.pem`, `.cloudflared/`는 git ignore 대상입니다.
- tunnel은 Grafana만 노출합니다.
- InfluxDB는 Cloudflare Tunnel ingress에 추가하지 않습니다.
- Grafana admin 비밀번호는 `.env` 또는 host secret으로만 관리합니다.
- public demo에서는 admin 경로 보호를 위해 Cloudflare Access 적용을 검토합니다.

## 참고

- Cloudflare Tunnel configuration file: https://developers.cloudflare.com/tunnel/advanced/local-management/configuration-file/
- Cloudflare Tunnel routing: https://developers.cloudflare.com/tunnel/routing/
- Cloudflare Tunnel Windows service: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/as-a-service/windows/
