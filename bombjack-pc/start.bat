@echo off
rem Mighty Bomb Jack offline launcher (fully portable - no installation needed)
rem Priority: bundled runtime\pythonw.exe -> system pythonw -> system python
rem NOTE: pass "." as serve dir; serve.py resolves it against its own folder,
rem       so no trailing-backslash quote issues here
cd /d "%~dp0"
if exist "runtime\pythonw.exe" (
    start "" "runtime\pythonw.exe" "serve.py" 9806 "."
    exit
)
where pythonw >nul 2>nul
if not errorlevel 1 (
    start "" pythonw "serve.py" 9806 "."
    exit
)
start "" python "serve.py" 9806 "."
exit
