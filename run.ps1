param([switch]$CheckOnly)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontend = Join-Path $root "frontend"
$backend = Join-Path $root "backend"

function Find-CommandPath([string]$name) {
    $command = Get-Command $name -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    return $null
}

$python = Find-CommandPath "python"
$node = Find-CommandPath "node"
$npm = Find-CommandPath "npm"

if (-not $python) { throw "Python was not found on PATH." }
if (-not $node) { throw "Node.js was not found on PATH." }
if (-not $npm) { throw "npm was not found on PATH." }

$postgresReady = Test-NetConnection -ComputerName "localhost" -Port 5432 -InformationLevel Quiet
if (-not $postgresReady) { throw "PostgreSQL is not reachable at localhost:5432. Start PostgreSQL and run this command again." }

if ($CheckOnly) {
    Write-Host "GeoInsight prerequisites are ready." -ForegroundColor Green
    Write-Host "Python: $python"
    Write-Host "Node:   $node"
    Write-Host "Postgres: localhost:5432"
    exit 0
}

$backendCommand = "Set-Location '$root'; & '$python' -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"
$backendCommand = "Set-Location '$root'; & '$python' -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001"
$frontendCommand = "Set-Location '$frontend'; npm run dev -- --host 127.0.0.1"

Start-Process powershell.exe -ArgumentList @("-NoExit", "-Command", $backendCommand) -WorkingDirectory $root
Start-Process powershell.exe -ArgumentList @("-NoExit", "-Command", $frontendCommand) -WorkingDirectory $root

Write-Host "GeoInsight is starting..." -ForegroundColor Green
Write-Host "Dashboard: http://127.0.0.1:5173/"
Write-Host "API docs:  http://127.0.0.1:8001/docs"
Write-Host "Validation: http://127.0.0.1:8001/api/v1/model/validation"