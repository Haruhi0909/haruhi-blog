@echo off
cd /d "%~dp0"

echo ========================================
echo   Chunri Blog - Push to GitHub
echo ========================================
echo.

git add .
git commit -m "update blog content"

echo.
echo Pushing to GitHub...
echo.

git push origin master
if %errorlevel% equ 0 goto success

echo.
echo Push failed, retrying (1/3)...
timeout /t 3 /nobreak >nul
git push origin master
if %errorlevel% equ 0 goto success

echo.
echo Push failed, retrying (2/3)...
timeout /t 5 /nobreak >nul
git push origin master
if %errorlevel% equ 0 goto success

echo.
echo Push failed, retrying (3/3)...
timeout /t 8 /nobreak >nul
git push origin master
if %errorlevel% equ 0 goto success

echo.
echo ========================================
echo   FAILED! Network or login issue.
echo   Please check your internet connection.
echo ========================================
pause
exit /b 1

:success
echo.
echo ========================================
echo   SUCCESS! Code pushed to GitHub.
echo   Vercel will auto-deploy in 1-2 min.
echo   Visit: https://haruhi-blog.vercel.app
echo ========================================
pause
