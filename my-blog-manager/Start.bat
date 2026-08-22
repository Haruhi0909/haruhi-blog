@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ========================================
echo   星辉云端控制台 - 启动中...
echo ========================================
echo.

:: 优先使用 Python 3.11（依赖已安装在此版本）
py -3.11 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [1/2] 找到 Python 3.11，正在启动...
    py -3.11 run_me.py
    if %errorlevel% neq 0 (
        echo.
        echo [错误] 启动失败！请截图上方错误信息。
        pause
        exit /b 1
    )
    goto end
)

:: 兜底：尝试默认 python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [1/2] 使用默认 Python，正在启动...
    python run_me.py
    if %errorlevel% neq 0 (
        echo.
        echo [错误] 启动失败！请截图上方错误信息。
        pause
        exit /b 1
    )
    goto end
)

echo [错误] 未找到 Python，请先安装 Python 3.10+ 并加入 PATH。
pause
exit /b 1

:end
echo.
echo [完成] 启动流程结束。
exit /b 0
