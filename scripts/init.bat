@echo off
REM ==================== XU-News-AI-RAG 初始化脚本 (Windows) ====================
setlocal enabledelayedexpansion

echo ==========================================
echo   XU-News-AI-RAG 环境初始化
echo ==========================================

REM -------------------- 检查必要工具 --------------------
echo.
echo 1. 检查必要工具...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未安装 Python 3
    exit /b 1
)

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未安装 Node.js
    exit /b 1
)

where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 警告: 未安装 Ollama，请手动安装
)

echo √ 工具检查完成

REM -------------------- 配置环境变量 --------------------
echo.
echo 2. 配置环境变量...

if not exist .env (
    echo 创建 .env 文件...
    (
        echo APP_ENV=development
        echo APP_DEBUG=true
        echo APP_PORT=5000
        echo DATABASE_URL=sqlite:///data/xu_news.db
        echo OLLAMA_HOST=http://127.0.0.1:11434
        echo OLLAMA_EMBEDDING_MODEL=mxbai-embed-large
        echo OLLAMA_LLM_MODEL=qwen2.5:7b
    ) > .env
    echo √ .env 文件已创建
) else (
    echo √ .env 文件已存在
)

REM -------------------- 后端初始化 --------------------
echo.
echo 3. 初始化后端...

cd backend

if not exist venv (
    echo 创建 Python 虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装后端依赖...
pip install -r requirements.txt -q

mkdir data data\faiss_indexes data\faiss_indexes\backup data\backup 2>nul
mkdir ..\logs 2>nul

echo √ 后端初始化完成

cd ..

REM -------------------- 前端初始化 --------------------
echo.
echo 4. 初始化前端...

cd frontend

if not exist node_modules (
    echo 安装前端依赖...
    call npm install
) else (
    echo √ 前端依赖已安装
)

if not exist .env.local (
    echo 创建前端 .env.local 文件...
    (
        echo VITE_API_BASE_URL=http://localhost:5000
        echo VITE_APP_TITLE=XU-News-AI-RAG
    ) > .env.local
)

echo √ 前端初始化完成

cd ..

REM -------------------- Ollama 配置 --------------------
echo.
echo 5. 配置 Ollama...

where ollama >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo 拉取 Embedding 模型...
    ollama pull mxbai-embed-large
    
    echo 拉取 LLM 模型...
    ollama pull qwen2.5:7b
    
    echo √ Ollama 模型配置完成
) else (
    echo 警告: Ollama 未安装
)

REM -------------------- 完成 --------------------
echo.
echo ==========================================
echo   √ 初始化完成！
echo ==========================================
echo.
echo 下一步:
echo   1. 启动开发环境: .\scripts\dev.bat
echo   2. 访问前端: http://localhost:3000
echo   3. 访问后端: http://localhost:5000
echo.

pause

