@echo off
REM ==================== XU-News-AI-RAG 开发环境启动脚本 (Windows) ====================

echo ==========================================
echo   XU-News-AI-RAG 开发环境启动
echo ==========================================

if not exist .env (
    echo 错误: 未找到 .env 文件，请先运行 .\scripts\init.bat
    exit /b 1
)

REM -------------------- 启动后端 --------------------
echo.
echo 1. 启动后端服务...

start "XU-News Backend" cmd /k "cd backend && venv\Scripts\activate && python run.py"

echo √ 后端服务已启动 (端口: 5000)

REM -------------------- 启动前端 --------------------
echo.
echo 2. 启动前端服务...

start "XU-News Frontend" cmd /k "cd frontend && npm run dev"

echo √ 前端服务已启动 (端口: 3000)

REM -------------------- 提示信息 --------------------
echo.
echo ==========================================
echo   √ 所有服务已启动！
echo ==========================================
echo.
echo 服务地址:
echo   - 前端: http://localhost:3000
echo   - 后端: http://localhost:5000
echo   - Ollama: http://localhost:11434
echo.
echo 查看日志请查看各服务窗口
echo.

pause

