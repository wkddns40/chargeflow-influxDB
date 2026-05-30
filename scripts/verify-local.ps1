$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    python -m pytest "backend\tests"
    python "tools\mockgen.py" all --profile smoke --seed 42 --end 2026-01-01T00:00:00Z

    Push-Location "frontend"
    try {
        npm run test
        npm run build
    }
    finally {
        Pop-Location
    }

    docker compose config | Out-Null

    Write-Host "Local verification complete."
}
finally {
    Pop-Location
}
