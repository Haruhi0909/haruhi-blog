@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ========================================
echo   春日博客 - 一键推送到线上
echo ========================================
echo.

git add .
git commit -m "更新博客内容"
git push

echo.
echo ========================================
echo   推送完成！Vercel 会自动更新线上博客
echo   等 1-2 分钟后访问 https://haruhi-blog.vercel.app
echo ========================================
pause
