# Grafana

Grafana is provisioned from:

```text
grafana/provisioning/datasources/influxdb.yaml
grafana/provisioning/dashboards/dashboards.yaml
grafana/dashboards/station_24h.json
```

Datasource:

```text
name: InfluxDB-Charger-Mock
uid: influxdb-charger-mock
query language: SQL
database: charger
url: http://influxdb3-core:8181
```

The datasource uses the Docker Compose service name. Grafana talks to InfluxDB over the internal Docker network; browsers and remote clients should not connect to InfluxDB directly.

Dashboard:

```text
uid: station-24h
title: Station 24h Timeline
variable: station_id
```

Iframe settings:

```text
GF_SECURITY_ALLOW_EMBEDDING=true
GF_AUTH_ANONYMOUS_ENABLED=true
GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer
GF_SERVER_ROOT_URL=${GRAFANA_ROOT_URL}
```

For local development, `GRAFANA_ROOT_URL` should be `http://localhost:3001`. For Cloudflare Tunnel, set it to the public tunnel URL and recreate the Grafana container.
