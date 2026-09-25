@echo off
setlocal EnableExtensions

cd /d "%~dp0"

python generate_html.py
if errorlevel 1 (
    echo generate_html.py failed.
    exit /b 1
)

python generate_html.py --all-markdown Research
if errorlevel 1 (
    echo Research HTML generation failed.
    exit /b 1
)

python update.py
if errorlevel 1 (
    echo update.py failed.
    exit /b 1
)

for /f "delims=" %%D in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set "UPDATE_DATE=%%D"
if not defined UPDATE_DATE (
    echo Failed to determine the update date.
    exit /b 1
)

git add --all
if errorlevel 1 (
    echo git add failed.
    exit /b 1
)

git diff --cached --quiet
if errorlevel 2 (
    echo Failed to check staged changes.
    exit /b 1
)
if not errorlevel 1 (
    echo No changes to commit. Pushing any pending commits.
    goto push_changes
)

git commit -m "update %UPDATE_DATE%"
if errorlevel 1 (
    echo git commit failed.
    exit /b 1
)

:push_changes
git push
if errorlevel 1 (
    echo git push failed.
    exit /b 1
)

echo HTML files and top-page links were updated, committed, and pushed.
exit /b 0
