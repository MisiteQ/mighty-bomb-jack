@echo off
rem Stop the Bomb Jack background server
cd /d "%~dp0"
if exist "server.pid" (
    for /f %%i in (server.pid) do taskkill /pid %%i /f
    del "server.pid"
    echo Server stopped.
) else (
    echo Server is not running.
)
