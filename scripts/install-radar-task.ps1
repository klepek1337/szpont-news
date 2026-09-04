param(
    [string]$TaskName = "Szpont News Radar",
    [string]$Instrument = "BTC-USDT-SWAP"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$RunnerScript = Join-Path $ProjectRoot "scripts\run-radar.ps1"
$PowerShellArguments = "-NoProfile -ExecutionPolicy Bypass -File `"$RunnerScript`" -Instrument $Instrument"
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $PowerShellArguments
$FirstRun = (Get-Date).Date.AddHours(2)
while ($FirstRun -le (Get-Date)) { $FirstRun = $FirstRun.AddHours(4) }
$Trigger = New-ScheduledTaskTrigger -Once -At $FirstRun `
    -RepetitionInterval (New-TimeSpan -Hours 4)
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Settings $Settings -Description "Szpont News market-risk report every four hours" `
    -Force | Out-Null
Write-Host "Scheduled task '$TaskName'. First run: $FirstRun"
