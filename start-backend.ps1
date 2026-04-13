# Start NOVA backend for local testing (SQLite by default).
# Install once:  py -3.8 -m venv .venv
#               .\.venv\Scripts\Activate.ps1
#               pip install -r requirements.txt

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

if (-not $env:DATABASE_URI) {
    $dbPath = (Join-Path $here "nova_local.db").Replace("\", "/")
    $env:DATABASE_URI = "sqlite:///$dbPath"
}

Write-Host "Using DATABASE_URI=$($env:DATABASE_URI)"

$venvPy = Join-Path $here ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "Create a venv first: py -3.8 -m venv .venv"
    Write-Host "Then: .\.venv\Scripts\Activate.ps1 ; pip install -r requirements.txt"
    exit 1
}

& $venvPy "create_tables.py"
& $venvPy "app.py"
