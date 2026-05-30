$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
    }

    python -m pip install -r "backend\requirements.txt"

    Push-Location "frontend"
    try {
        npm install
    }
    finally {
        Pop-Location
    }

    python "tools\mockgen.py" all --profile smoke --seed 42
    docker compose config | Out-Null

    Write-Host "Local setup complete."
}
finally {
    Pop-Location
}
