@echo off
cd /d "%~dp0"
title ShareDeal Price Tracker

:MENU
cls
echo ============================================
echo      SHAREDEAL PRICE TRACKER
echo      sharedealnow.com daily price monitor
echo ============================================
echo.
echo  [0] Scrape Live + Open Dashboard
echo  [1] Scrape Live (API, one pass)
echo  [2] Watch Mode (re-scrape every N minutes)
echo  [3] Open Dashboard (serve + browser)
echo  [4] Seed baseline from HAR (extract_har.py, one-time)
echo  [5] Show HAR Analysis Summary
echo  [6] Open Website + API in Browser
echo  [Q] Quit
echo.

set /p choice="Select option: "

if /I "%choice%"=="0" goto SCRAPE_SERVE
if /I "%choice%"=="1" goto SCRAPE
if /I "%choice%"=="2" goto WATCH
if /I "%choice%"=="3" goto SERVE
if /I "%choice%"=="4" goto EXTRACT
if /I "%choice%"=="5" goto ANALYSIS
if /I "%choice%"=="6" goto WEBSITES
if /I "%choice%"=="Q" goto QUIT
goto MENU

:SCRAPE_SERVE
echo.
echo === Scraping live API... ===
python scraper.py
if %ERRORLEVEL% neq 0 (
    echo Scrape failed. Check errors above.
    pause
    goto MENU
)
echo.
echo === Starting dashboard server... ===
start /B python -m http.server 8765
timeout /t 2 /nobreak >nul
start "" "http://localhost:8765/frontend/"
echo Dashboard: http://localhost:8765/frontend/  (Ctrl+C in server window to stop)
pause
goto MENU

:SCRAPE
echo.
echo === Scraping live API... ===
python scraper.py
if %ERRORLEVEL% neq 0 (
    echo Scrape failed. Check errors above.
)
pause
goto MENU

:WATCH
echo.
set /p mins="Minutes between scrapes [60]: "
if "%mins%"=="" set mins=60
echo === Watching (scrape every %mins% min) — Ctrl+C to stop ===
python scraper.py --watch %mins%
pause
goto MENU

:SERVE
echo.
echo === Starting dashboard server on http://localhost:8765 ===
start /B python -m http.server 8765
timeout /t 2 /nobreak >nul
start "" "http://localhost:8765/frontend/"
echo Dashboard: http://localhost:8765/frontend/  (Ctrl+C in server window to stop)
pause
goto MENU

:EXTRACT
echo.
echo === Extracting baseline from HAR (one-time seed) ===
python extract_har.py
if %ERRORLEVEL% neq 0 (
    echo Extraction failed. Check errors above.
)
pause
goto MENU

:ANALYSIS
echo.
echo === HAR Analysis Summary ===
python -c "import json; har=json.load(open('sharedealnow.com_2026_07_30_04_00_04.har',encoding='utf-8')); e=har['log']['entries']; urls=[x['request']['url'] for x in e if 'sharedealnow.com/api' in x['request']['url']]; print(f'Entries: {len(e)}'); print(f'API calls: {len(urls)}'); [print('  '+u.split('sharedealnow.com')[1]) for u in sorted(set(urls))]"
pause
goto MENU

:WEBSITES
echo.
echo Opening ShareDeal website and API...
start "" "https://sharedealnow.com"
start "" "https://sharedealnow.com/api/v1/home"
timeout /t 2 >nul
goto MENU

:QUIT
echo.
echo Goodbye!
exit /b 0