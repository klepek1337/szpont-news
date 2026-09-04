$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VirtualEnvironmentPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $VirtualEnvironmentPython)) {
    py -3.11 -m venv (Join-Path $ProjectRoot ".venv")
}

& $VirtualEnvironmentPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
& $VirtualEnvironmentPython -m pip install -e "${ProjectRoot}[dev]"
if ($LASTEXITCODE -ne 0) { throw "Szpont News installation failed." }

$EventFile = Join-Path $ProjectRoot "config\events.json"
if (-not (Test-Path $EventFile)) {
    Copy-Item (Join-Path $ProjectRoot "config\events.example.json") $EventFile
}
$FeedFile = Join-Path $ProjectRoot "config\feeds.json"
if (-not (Test-Path $FeedFile)) {
    Copy-Item (Join-Path $ProjectRoot "config\feeds.example.json") $FeedFile
}

Write-Host "Szpont News installed."
Write-Host "Set SZPONT_TELEGRAM_BOT_TOKEN and SZPONT_TELEGRAM_CHAT_ID."
Write-Host "Run .\scripts\run-radar.ps1"
