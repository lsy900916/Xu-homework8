#!/bin/bash
# ==================== XU-News-AI-RAG 初始化脚本 ====================
# 用途: 初始化开发环境

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  XU-News-AI-RAG 环境初始化"
echo "=========================================="

# -------------------- 检查必要工具 --------------------
echo "1. 检查必要工具..."

command -v python3 >/dev/null 2>&1 || { echo "错误: 未安装 Python 3" >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "错误: 未安装 Node.js" >&2; exit 1; }
command -v ollama >/dev/null 2>&1 || { echo "警告: 未安装 Ollama，请手动安装" >&2; }

echo "✓ 工具检查完成"

# -------------------- 配置环境变量 --------------------
echo ""
echo "2. 配置环境变量..."

if [ ! -f .env ]; then
    echo "创建 .env 文件..."
    cat > .env << 'EOF'
APP_ENV=development
APP_DEBUG=true
APP_PORT=5000
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
DATABASE_URL=sqlite:///data/xu_news.db
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large
OLLAMA_LLM_MODEL=qwen2.5:7b
CRAWLER_USER_AGENT=XU-News-Bot/1.0 (+https://xu-news.com/bot; contact@xu-news.com)
CRAWLER_RATE_LIMIT=2
LOG_LEVEL=INFO
EOF
    echo "✓ .env 文件已创建"
else
    echo "✓ .env 文件已存在"
fi

# -------------------- 后端初始化 --------------------
echo ""
echo "3. 初始化后端..."

cd backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装后端依赖..."
pip install -r requirements.txt -q

# 创建必要目录
mkdir -p data data/faiss_indexes data/faiss_indexes/backup data/backup
mkdir -p ../logs

echo "✓ 后端初始化完成"

cd ..

# -------------------- 前端初始化 --------------------
echo ""
echo "4. 初始化前端..."

cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
else
    echo "✓ 前端依赖已安装"
fi

# 配置环境变量
if [ ! -f .env.local ]; then
    echo "创建前端 .env.local 文件..."
    cat > .env.local << EOF
VITE_API_BASE_URL=http://localhost:5000
VITE_APP_TITLE=XU-News-AI-RAG
VITE_PAGE_SIZE=20
EOF
fi

echo "✓ 前端初始化完成"

cd ..

# -------------------- Ollama 配置 --------------------
echo ""
echo "5. 配置 Ollama..."

if command -v ollama >/dev/null 2>&1; then
    echo "拉取 Embedding 模型..."
    ollama pull mxbai-embed-large || echo "警告: Embedding 模型拉取失败"
    
    echo "拉取 LLM 模型..."
    ollama pull qwen2.5:7b || echo "警告: LLM 模型拉取失败"
    
    echo "✓ Ollama 模型配置完成"
else
    echo "⚠ Ollama 未安装，请手动安装并拉取模型:"
    echo "  1. 访问 https://ollama.ai/download"
    echo "  2. 安装完成后执行:"
    echo "     ollama pull mxbai-embed-large"
    echo "     ollama pull qwen2.5:7b"
fi

# -------------------- 完成 --------------------
echo ""
echo "=========================================="
echo "  ✓ 初始化完成！"
echo "=========================================="
echo ""
echo "下一步:"
echo "  1. 启动开发环境: ./scripts/dev.sh"
echo "  2. 访问前端: http://localhost:3000"
echo "  3. 访问后端: http://localhost:5000"
echo "  4. 查看文档: docs/OPS_GUIDE.md"
echo ""

