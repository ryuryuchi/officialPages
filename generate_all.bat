@echo off
setlocal

cd /d "%~dp0"

python generate_html.py
if errorlevel 1 (
    echo generate_html.py failed.
    exit /b 1
)

python update.py
if errorlevel 1 (
    echo update.py failed.
    exit /b 1
)

echo All HTML files and top-page links were updated.
exit /b 0
