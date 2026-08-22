@echo off
cd /d "%~dp0"

echo ========================================
echo   Chunri Blog - Push to GitHub
echo ========================================
echo.

git add .
git commit -m "update blog content"
git push

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   Push success! Vercel will auto deploy
    echo   Wait 1-2 min, then visit:
    echo   https://haruhi-blog.vercel.app
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   Push FAILED! Check network or login
    echo ========================================
)

pause
