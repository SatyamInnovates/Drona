@echo off
cd /d "%~dp0Backend(main files)"
start "Drona server" cmd /k "python -m uvicorn server2:app --app-dir . --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8000/Frontend/"