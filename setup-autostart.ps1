# ChemLab Bot — автозапуск через Windows Task Scheduler
# Запустить один раз от имени Администратора

$botDir = "D:\projects\conference\bot"
$python = "D:\projects\conference\bot\.venv\Scripts\python.exe"
$script = "D:\projects\conference\bot\main.py"
$envFile = "D:\projects\conference\.env"
$taskName = "ChemLabBot"

# Проверка прав
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ОШИБКА: Запустите скрипт от имени Администратора!" -ForegroundColor Red
    pause
    exit 1
}

# Удалить старую задачу если есть
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Wrapper скрипт — читает .env и запускает бота в цикле
$wrapperPath = "D:\projects\conference\bot\run-bot.ps1"
@'
# Load .env file
$envFile = "D:\projects\conference\.env"
Get-Content $envFile | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
    $parts = $_ -split '=', 2
    [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process')
}

Set-Location 'D:\projects\conference\bot'

while ($true) {
    Write-Host "[$([DateTime]::Now)] Starting ChemLab Bot..."
    $proc = Start-Process -FilePath 'D:\projects\conference\bot\.venv\Scripts\python.exe' `
        -ArgumentList 'D:\projects\conference\bot\main.py' `
        -PassThru -NoNewWindow -Wait
    Write-Host "[$([DateTime]::Now)] Bot stopped (code $($proc.ExitCode)). Restarting in 5s..."
    Start-Sleep -Seconds 5
}
'@ | Out-File -FilePath $wrapperPath -Encoding UTF8

# Настройка задачи
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$wrapperPath`"" `
    -WorkingDirectory $botDir

$triggers = @(
    $(New-ScheduledTaskTrigger -AtStartup),
    $(New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME)
)

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -RunLevel Highest `
    -LogonType Interactive

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $triggers `
    -Settings $settings `
    -Principal $principal `
    -Force

# Запустить сразу
Write-Host "Starting bot now..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 3

$state = (Get-ScheduledTask -TaskName $taskName).State
Write-Host ""
Write-Host "ChemLab Bot настроен! Статус: $state" -ForegroundColor Green
Write-Host "Бот будет запускаться автоматически при каждом включении." -ForegroundColor White
Write-Host ""
Write-Host "Управление:" -ForegroundColor Yellow
Write-Host "  Остановить: Stop-ScheduledTask -TaskName '$taskName'"
Write-Host "  Запустить:  Start-ScheduledTask -TaskName '$taskName'"
Write-Host "  Статус:     Get-ScheduledTask -TaskName '$taskName'"
pause
