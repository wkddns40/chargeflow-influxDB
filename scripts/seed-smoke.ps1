param(
    [ValidateSet("smoke", "seoul-gyeonggi", "dev", "perf")]
    [string] $Profile = "smoke",
    [int] $Seed = 42,
    [int] $InfluxPort = 8181,
    [string] $InfluxHost = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    docker compose up -d influxdb3-core

    $healthUrl = "http://$InfluxHost`:$InfluxPort/health"
    $ready = $false
    for ($i = 0; $i -lt 60; $i++) {
        try {
            Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 2 | Out-Null
            $ready = $true
            break
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }

    if (-not $ready) {
        throw "InfluxDB did not become ready at $healthUrl"
    }

    python "tools\mockgen.py" all --profile $Profile --seed $Seed
    python "tools\seed_influx.py" --profile $Profile --seed $Seed --url "http://$InfluxHost`:$InfluxPort"

    Write-Host "Mock data seeded for profile '$Profile'."
}
finally {
    Pop-Location
}
