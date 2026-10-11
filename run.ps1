$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path .\.venv\Scripts\python.exe)) {
    python -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install -q -e .
.\.venv\Scripts\python.exe -m adewi
Write-Host "Done. Figures: results\figures  Tables: results\tables"
