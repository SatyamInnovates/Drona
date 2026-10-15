@echo off
set "DRONA_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%DRONA_PYTHON%" (
  echo Drona has not been installed yet. Run Install-Drona.ps1 from this folder first.
  pause
  exit /b 1
)
cd /d "%~dp0Backend(main files)"
start "Drona server" cmd /k ""%DRONA_PYTHON%" -m uvicorn server2:app --app-dir . --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8000/Frontend/"
