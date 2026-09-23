# One-time setup. Uses the Python interpreter installed on the current machine.
$projectRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $projectRoot ".marine-env"
$python = Join-Path $envPath "Scripts\python.exe"
$systemPython = (Get-Command python -ErrorAction Stop).Source

if (-not (Test-Path (Join-Path $projectRoot ".env"))) {
    Copy-Item (Join-Path $projectRoot ".env.example") (Join-Path $projectRoot ".env")
    Write-Host "Created .env from .env.example. Review it before deployment." -ForegroundColor Cyan
}

if (-not (Test-Path $python)) {
    & $systemPython -m venv $envPath
}

& $python -m pip install --upgrade pip
& $python -m pip install -r (Join-Path $projectRoot "requirements.txt")
& $python -c "import pandas, streamlit, ultralytics; print('Marine Sentinel environment is ready.')"
