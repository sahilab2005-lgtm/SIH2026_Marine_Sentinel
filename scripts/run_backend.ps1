# Starts the local FastAPI inference and reporting service.
$projectRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $projectRoot ".marine-env"
$python = Join-Path $envPath "Scripts\python.exe"
$envFile = Join-Path $projectRoot ".env"

if (-not (Test-Path $python)) {
    Write-Host "Environment missing. Run .\scripts\setup_dashboard.ps1 once first." -ForegroundColor Yellow
    exit 1
}

Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#=]+?)\s*=\s*(.*)\s*$') { Set-Item -Path "Env:$($matches[1].Trim())" -Value $matches[2].Trim() }
}
$env:PYTHONPATH = Join-Path $projectRoot "src"
& $python -m uvicorn marine_sentinel.api.main:app --host $env:API_HOST --port $env:API_PORT --reload
