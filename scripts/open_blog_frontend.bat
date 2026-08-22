@echo off
netstat -ano | findstr ":3000 " | findstr LISTENING >nul
if %errorlevel%==0 (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=http://localhost:3000
    exit /b
)
cd /d "E:\Haruhi\XinghuisamaBlogs-main\XHBlogs"
start /b npm run dev
:wait
ping -n 2 127.0.0.1 >nul
netstat -ano | findstr ":3000 " | findstr LISTENING >nul
if errorlevel 1 goto wait
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=http://localhost:3000
