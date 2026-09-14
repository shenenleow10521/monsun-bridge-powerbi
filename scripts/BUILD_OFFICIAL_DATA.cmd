@echo off
cd /d "%~dp0.."
py -3 scripts\build_official_data.py
if errorlevel 1 (
  echo Build failed. Keep the error message for diagnosis.
  pause
  exit /b 1
)
echo Set OfficialDataFolder in Power BI to the printed processed path.
pause
