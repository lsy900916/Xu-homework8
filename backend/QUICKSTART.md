# Flask Backend 快速启动指南

## 🚀 5 分钟快速开始

### 1. 安装 Ollama 并拉取模型

```bash
# 安装 Ollama
# Windows: https://ollama.ai/download
# Linux/Mac: curl -fsSL https://ollama.ai/install.sh | sh

# 拉取模型
ollama pull qwen2.5:3b
ollama pull mxbai-embed-large

# 验证
ollama list
```

### 2. 安装 Python 依赖

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 创建管理员账户

```bash
python scripts/create_admin.py --email admin@xu-news.com --password Admin123
```

### 5. 启动服务

```bash
python app.py
```

### 6. 测试 API

```bash
# 健康检查
curl http://localhost:5000/api/health

# 注册用户
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"User1234"}'

# 登录获取 Token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"User1234"}'
```

## 📝 测试数据入库

```bash
# 获取 Token（从登录响应中复制）
export TOKEN="eyJhbGci..."

# 入库测试数据
curl -X POST http://localhost:5000/api/ingest/structured \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "data": [
      {
        "title": "OpenAI 发布 GPT-5",
        "content": "OpenAI 今日宣布发布最新一代语言模型 GPT-5，性能相比 GPT-4 大幅提升。新模型在多个基准测试中刷新了记录，特别是在代码生成和多语言理解方面表现出色。GPT-5 采用了全新的训练方法，大幅降低了计算成本...",
        "url": "https://example.com/news/gpt5",
        "source": "科技日报",
        "category": "科技"
      }
    ]
  }'
```

## 🔍 测试 RAG 问答

```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question":"最近关于 AI 的新闻有哪些？"}'
```

## 🧪 运行测试

```bash
# 所有测试
pytest tests/ -v

# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# 覆盖率
pytest tests/ --cov=. --cov-report=html
```

## 📊 目录结构

```
backend/
├── app.py              # Flask 入口
├── config.py           # 配置
├── core/               # RAG 核心
├── db/                 # 数据库
├── auth/               # 认证
├── apis/               # API 路由
├── services/           # 服务层
├── tests/              # 测试
├── scripts/            # 脚本
├── storage/            # 数据存储
│   ├── app.db          # SQLite
│   └── faiss_index/    # FAISS 索引
└── requirements.txt    # 依赖
```

## ⚙️ 环境变量

在项目根目录创建 `.env` 文件：

```bash
# Ollama
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:3b

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production

# 百度搜索（可选）
BAIDU_API_KEY=your-baidu-api-key
BAIDU_SECRET_KEY=your-baidu-secret-key
```

## 🐛 常见问题

### Ollama 连接失败

```bash
# 检查 Ollama 是否运行
curl http://127.0.0.1:11434/api/version

# 启动 Ollama
ollama serve
```

### 模型下载慢

```bash
# 使用国内镜像（可选）
export OLLAMA_HOST=https://ollama-mirror.example.com
ollama pull qwen2.5:3b
```

### 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 使用国内源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📚 API 文档

启动服务后访问：http://localhost:5000/api/health

完整 API 文档见：`docs/API_SPEC.md`

## 🔗 相关链接

- Ollama: https://ollama.ai
- LangChain: https://python.langchain.com
- FAISS: https://faiss.ai
- Flask: https://flask.palletsprojects.com
