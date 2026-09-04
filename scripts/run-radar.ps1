param(
    [string]$Instrument = "BTC-USDT-SWAP",
    [string]$EventFile = "config\events.json",
    [string]$FeedFile = "config\feeds.json"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonPath = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonPath)) {
    throw "Virtual environment not found. Run scripts\setup.ps1 first."
}

Push-Location $ProjectRoot
try {
    & $PythonPath -m szpont_news report `
        --instrument $Instrument `
        --events $EventFile `
        --feeds $FeedFile `
        --telegram
    if ($LASTEXITCODE -ne 0) { throw "Szpont News report failed." }
}
finally {
    Pop-Location
}
