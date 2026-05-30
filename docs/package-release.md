# Package Release

Create a source release package:

```powershell
.\scripts\package-release.ps1 -Version 0.1.0
```

Outputs:

```text
dist/package/chargeflow-influxDB-v0.1.0-source.zip
dist/package/SHA256SUMS.txt
```

Included:

- source code
- Docker Compose
- Grafana provisioning
- docs
- scripts
- `.env.example`

Excluded:

- `.env`
- generated mock data
- InfluxDB runtime volume
- Grafana runtime DB
- `node_modules`
- `.venv`
- build output
