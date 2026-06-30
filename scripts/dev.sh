#!/bin/bash
# ==================== XU-News-AI-RAG 开发环境启动脚本 ====================

set -e

echo "=========================================="
echo "  XU-News-AI-RAG 开发环境启动"
echo "=========================================="

# 检查是否已初始化
if [ ! -f .env ]; then
    echo "错误: 未找到 .env 文件，请先运行 ./scripts/init.sh"
    exit 1
fi

# -------------------- 启动后端 --------------------
echo ""
echo "1. 启动后端服务..."

cd backend
source venv/bin/activate

# 后台运行
python run.py &
BACKEND_PID=$!

echo "✓ 后端服务已启动 (PID: $BACKEND_PID, 端口: 5000)"

cd ..

# -------------------- 启动前端 --------------------
echo ""
echo "2. 启动前端服务..."

cd frontend

# 后台运行
npm run dev &
FRONTEND_PID=$!

echo "✓ 前端服务已启动 (PID: $FRONTEND_PID, 端口: 3000)"

cd ..

# -------------------- 提示信息 --------------------
echo ""
echo "=========================================="
echo "  ✓ 所有服务已启动！"
echo "=========================================="
echo ""
echo "服务地址:"
echo "  - 前端: http://localhost:3000"
echo "  - 后端: http://localhost:5000"
echo "  - Ollama: http://localhost:11434"
echo ""
echo "进程 ID:"
echo "  - 后端: $BACKEND_PID"
echo "  - 前端: $FRONTEND_PID"
echo ""
echo "停止服务:"
echo "  - 后端: kill $BACKEND_PID"
echo "  - 前端: kill $FRONTEND_PID"
echo "  - 或按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

wait

