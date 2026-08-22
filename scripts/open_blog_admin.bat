@echo off
netstat -ano > "%temp%\port_check.tmp"
findstr ":58643 " "%temp%\port_check.tmp" | findstr LISTENING >nul
set "be_ok=%errorlevel%"
findstr ":3001 " "%temp%\port_check.tmp" | findstr LISTENING >nul
set "fe_ok=%errorlevel%"
del "%temp%\port_check.tmp"
if %be_ok%==0 if %fe_ok%==0 (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=http://localhost:3001
    exit /b
)
if %be_ok%==1 (
    cd /d "E:\Haruhi\XinghuisamaBlogs-main\my-blog-manager"
    start /b cmd /c "set PYTHONPATH=C:\Users\admin\AppData\Local\Temp\pydeps;E:\Haruhi\XinghuisamaBlogs-main\my-blog-manager && python -m uvicorn cms_core.main:app --host 127.0.0.1 --port 58643"
)
if %fe_ok%==1 (
    cd /d "E:\Haruhi\XinghuisamaBlogs-main\my-blog-manager"
    start /b npm run dev
)
:wait
ping -n 2 127.0.0.1 >nul
netstat -ano | findstr ":3001 " | findstr LISTENING >nul
if errorlevel 1 goto wait
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=http://localhost:3001
