$ErrorActionPreference = "Stop"
$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $backendDir
if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    throw "Create a local virtual environment and install requirements.txt before starting the API."
}
& ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
