@echo off
set "DRONA_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%DRONA_PYTHON%" (
  echo Drona has not been installed yet. Run Install-Drona.ps1 from this folder first.
  pause
  exit /b 1
)
REM Reuse the server if another Drona window already has port 8000.
powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/Frontend/' -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }"
if not errorlevel 1 (
  start "" "http://127.0.0.1:8000/Frontend/"
  exit /b 0
)
cd /d "%~dp0Backend(main files)"
start "Drona server" cmd /k ""%DRONA_PYTHON%" -m uvicorn server2:app --app-dir . --host 127.0.0.1 --port 8000"
powershell -NoProfile -Command "$deadline = (Get-Date).AddSeconds(25); do { try { Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/Frontend/' -TimeoutSec 1 | Out-Null; exit 0 } catch { Start-Sleep -Milliseconds 500 } } while ((Get-Date) -lt $deadline); exit 1"
if errorlevel 1 (
  echo Drona did not respond within 25 seconds. Check the Drona server window for an error.
  pause
  exit /b 1
)
start "" "http://127.0.0.1:8000/Frontend/"
