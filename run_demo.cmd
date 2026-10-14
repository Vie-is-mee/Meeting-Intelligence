@echo off
setlocal
echo Recorded demo: http://127.0.0.1:5501
echo No API key or extra Python packages required. Press Ctrl+C to stop.
if exist "I:\Python\python.exe" (
    "I:\Python\python.exe" -m http.server 5501 --bind 127.0.0.1 --directory "%~dp0frontend"
) else (
    python -m http.server 5501 --bind 127.0.0.1 --directory "%~dp0frontend"
)
if errorlevel 1 pause
endlocal
