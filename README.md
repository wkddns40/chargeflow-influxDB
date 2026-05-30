# chargeflow-influxDB

`chargeflow-influxDB`는 ChargeFlow 리팩토링 흐름의 세 번째 단계 프로젝트입니다.

```text
D:\fleet\ev-charging
  -> 기존 EV 충전소 대시보드 원형

D:\fleet\chargeflow-kr
  -> 한국형 EV 충전소 지도 프론트엔드 중심 리팩토링

D:\fleet\chargeflow-influxDB
  -> chargeflow-kr 프론트엔드에 붙일 InfluxDB/Grafana 시각화 데모 런타임
```

이 프로젝트의 핵심은 `chargeflow-kr`의 프론트엔드 경험을 유지하면서, 충전소 마커 클릭 시 InfluxDB 시계열 데이터를 Grafana iframe으로 보여주는 데모를 검증하는 것입니다.

## 목표

```text
chargeflow-kr frontend shell
  -> 한국 EV 충전소 지도
  -> 마커 선택
  -> 충전소 상세 패널
  -> Grafana iframe timeline

chargeflow-influxDB runtime
  -> FastAPI station API
  -> Grafana iframe URL API
  -> InfluxDB 3 Core mock 시계열
  -> Grafana OSS dashboard
```

최종 방향은 `chargeflow-kr` 프론트엔드의 MAP UX 기반을 유지하면서, 백엔드는 `chargeflow-influxDB`의 InfluxDB/Grafana 구조를 붙이는 것입니다.

## 리팩토링 기준

`chargeflow-influxDB`에서 검증할 기준은 다음과 같습니다.

1. `chargeflow-kr`의 지도 UX를 재사용합니다.
2. Ask 검색은 유지하되, 초기에는 얇은 station metadata 검색으로 시작합니다.
3. 마커 클릭 후 상세 패널은 Grafana iframe을 중심으로 구성합니다.
4. InfluxDB는 충전기 상태, 전력, 가용률 시계열 데이터를 담당합니다.
5. Grafana는 시계열 표준 시각화 전용 레이어로 둡니다.

## 검증

Backend:

```powershell
python -m pytest backend/tests
```

Frontend:

```powershell
cd frontend
npm run typecheck
npm test
npm run build
```

Runtime smoke:

```text
1. 프론트엔드 접속
2. 충전소 마커 선택
3. Grafana iframe 로드 확인
4. iframe URL에 var-station_id=<선택 station> 포함 확인
5. Grafana panel에 no data가 없는지 확인
6. iframe fullscreen 진입/복귀 확인
```
