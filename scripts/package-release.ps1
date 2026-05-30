param(
    [Parameter(Mandatory = $true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $PSScriptRoot
$PackageRoot = Join-Path $Root "dist\package"
$Name = "chargeflow-influxDB-v$Version-source"
$TempRoot = Join-Path $PackageRoot $Name
$ZipPath = Join-Path $PackageRoot "$Name.zip"
$ChecksumPath = Join-Path $PackageRoot "SHA256SUMS.txt"
$CheckRoot = Join-Path $PackageRoot "check"

$RootResolved = (Resolve-Path $Root).Path
New-Item -ItemType Directory -Force -Path $PackageRoot | Out-Null

foreach ($path in @($TempRoot, $ZipPath, $ChecksumPath, $CheckRoot)) {
    if (Test-Path $path) {
        $resolved = (Resolve-Path $path).Path
        if (-not $resolved.StartsWith($RootResolved, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove path outside project: $resolved"
        }
        Remove-Item -LiteralPath $path -Recurse -Force
    }
}

New-Item -ItemType Directory -Force -Path $TempRoot | Out-Null

$excludeDirs = @(
    ".git",
    "dist",
    "data\generated",
    "data\influxdb",
    "data\influxdb-plugins",
    "data\grafana",
    "frontend\node_modules",
    "frontend\dist",
    "logs",
    "backend\.venv",
    ".venv",
    "__pycache__"
) | ForEach-Object { Join-Path $Root $_ }

$excludeFiles = @(".env", "*.lp", "*.tsbuildinfo")

robocopy $Root $TempRoot /E /XD $excludeDirs /XF $excludeFiles /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -gt 7) {
    throw "robocopy failed with exit code $LASTEXITCODE"
}

Compress-Archive -Path (Join-Path $TempRoot "*") -DestinationPath $ZipPath -Force
$hash = Get-FileHash -Algorithm SHA256 $ZipPath
"$($hash.Hash.ToLowerInvariant())  $(Split-Path -Leaf $ZipPath)" | Set-Content -Encoding ascii $ChecksumPath

Expand-Archive -Path $ZipPath -DestinationPath $CheckRoot -Force
if (-not (Test-Path (Join-Path $CheckRoot "README.md"))) {
    throw "Package smoke check failed: README.md missing"
}
docker compose -f (Join-Path $CheckRoot "docker-compose.yml") config | Out-Null

Write-Host "Package created:"
Write-Host $ZipPath
Write-Host $ChecksumPath
