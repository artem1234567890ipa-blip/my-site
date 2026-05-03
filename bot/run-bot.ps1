$envFile = "D:\projects\conference\.env"
Get-Content $envFile | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
    $parts = $_ -split '=', 2
    [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process')
}
Set-Location 'D:\projects\conference\bot'
while ($true) {
    $proc = Start-Process -FilePath 'D:\projects\conference\bot\.venv\Scripts\python.exe' -ArgumentList 'D:\projects\conference\bot\main.py' -PassThru -NoNewWindow -Wait
    Start-Sleep -Seconds 5
}
