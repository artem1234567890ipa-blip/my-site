@echo off
title ChemLab Bot
echo Starting ChemLab Bot...
cd /d D:\projects\conference\bot

REM Load secrets from .env file (not stored in git)
for /f "tokens=1,2 delims==" %%a in (D:\projects\conference\.env) do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" set %%a=%%b
)

:loop
echo [%time%] Bot running...
.venv\Scripts\python.exe main.py
echo [%time%] Bot crashed, restarting in 3 seconds...
timeout /t 3 /nobreak
goto loop
