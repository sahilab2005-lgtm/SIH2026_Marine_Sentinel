# Starts Marine Sentinel with the dedicated Python 3.12 environment.
$projectRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $projectRoot ".marine-env"
$python = Join-Path $envPath "Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "Environment missing. Run setup_dashboard.ps1 once first." -ForegroundColor Yellow
    exit 1
}

& $python -m streamlit run (Join-Path $projectRoot "app.py")
