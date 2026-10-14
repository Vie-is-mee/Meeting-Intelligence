@echo off
setlocal
cd /d "%~dp0"
if exist "I:\Python\python.exe" (
    "I:\Python\python.exe" -X utf8 "%~dp0web.py" %*
) else (
    python -X utf8 "%~dp0web.py" %*
)
if errorlevel 1 (
    echo.
    echo Server could not start. Read the error above.
    pause
)
endlocal
