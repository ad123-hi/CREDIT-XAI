@echo off
setlocal
cd /d "%~dp0"

REM ---------- build frontend if needed ----------
if not exist "%~dp0frontend\dist" (
    echo Building frontend...
    cd /d "%~dp0frontend"
    call npm run build
)

REM ---------- start FastAPI ----------
start "FastAPI Backend" powershell -NoExit -Command "Set-Location -LiteralPath '%~dp0backend'; python app.py"

REM ---------- start static server ----------
start "Frontend UI" powershell -NoExit -Command "Set-Location -LiteralPath '%~dp0frontend'; npx serve -s dist -l 3000"

echo.
echo ==========================================================
echo  FastAPI backend  -> http://127.0.0.1:8000
echo  Frontend UI    -> http://localhost:3000
echo ==========================================================
pause