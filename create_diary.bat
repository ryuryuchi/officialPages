@echo off
setlocal

cd /d "%~dp0"

python create_diary.py
if errorlevel 1 (
    echo create_diary.py failed.
    exit /b 1
)

exit /b 0
