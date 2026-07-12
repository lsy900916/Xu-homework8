# XU-News-AI-RAG Backend

Flask + RAG 完整后端实现

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 并修改：

```bash
cp ../.env.example .env
```

关键配置：

- `OLLAMA_HOST`: Ollama 服务地址
- `OLLAMA_MODEL`: qwen2.5:3b
- `JWT_SECRET_KEY`: JWT 密钥

### 3. 初始化数据库

```bash
python -c "from db.models import init_db; init_db()"
```

### 4. 启动 Ollama

```bash
# 拉取模型
ollama pull qwen2.5:3b

# 启动 Ollama 服务（如未自动启动）
ollama serve
```

### 5. 启动后端服务

```bash
python app.py
```

访问：http://localhost:5000

## 📁 项目结构

```
backend/
├── app.py                  # Flask 应用入口
├── config.py               # 配置管理
│
├── core/                   # RAG 核心
│   ├── embeddings.py       # all-MiniLM-L6-v2
│   ├── reranker.py         # ms-marco-MiniLM-L-6-v2
│   ├── vectorstore.py      # FAISS 管理
│   ├── llm.py              # Ollama 接入
│   └── rag.py              # RAG 流程
│
├── db/                     # 数据库
│   ├── models.py           # SQLAlchemy 模型
│   ├── schema.sql          # 初始化脚本
│   └── dao.py              # 数据访问对象
│
├── auth/                   # 认证
│   └── jwt.py              # JWT 登录/注册
│
├── apis/                   # API 路由
│   ├── health.py           # 健康检查
│   ├── ingest.py           # 数据入库
│   ├── search.py           # RAG 问答
│   └── reports.py          # 聚类/关键词
│
├── services/               # 服务层
│   ├── crawlers.py         # 爬虫扩展
│   └── search_fallback.py  # 百度搜索
│
├── tests/                  # 测试
│   ├── unit/
│   └── integration/
│
├── storage/                # 数据存储
│   ├── app.db              # SQLite 数据库
│   └── faiss_index/        # FAISS 索引
│
├── requirements.txt        # 依赖
└── README.md               # 本文件
```

## 📡 API 端点

### 认证

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

### 数据入库

- `POST /api/ingest/structured` - 结构化数据入库（Excel/JSON）
- `POST /api/ingest/unstructured` - 非结构化数据入库（文本/HTML）

### RAG 问答

- `POST /api/ask` - RAG 问答

### 报告

- `GET /api/report/clusters` - 聚类分析
- `GET /api/report/topkeywords` - Top10 关键词

### 系统

- `GET /api/health` - 健康检查

## 🔧 核心技术

### Embedding

- 模型：`sentence-transformers/all-MiniLM-L6-v2`
- 维度：384
- 批量大小：32

### Reranker

- 模型：`cross-encoder/ms-marco-MiniLM-L-6-v2`
- Top-K：5（重排后）

### LLM

- 引擎：Ollama
- 模型：qwen2.5:3b
- 温度：0.7
- 最大 Tokens：2048

### 向量库

- FAISS IndexFlatL2（精确检索）
- 存储路径：`storage/faiss_index/`

### 数据库

- SQLite
- 表：users, articles, chunks, query_logs, system_meta

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行单元测试
pytest tests/unit/ -v

# 运行集成测试
pytest tests/integration/ -v

# 测试覆盖率
pytest tests/ --cov=. --cov-report=html
```

## 📝 开发

### 添加新的 API

1. 在 `apis/` 下创建蓝图
2. 在 `app.py` 中注册蓝图
3. 添加对应的测试

### 数据库迁移

```python
# 修改 models.py 后
from db.models import Base, engine
Base.metadata.create_all(engine)
```

## 🔐 安全

- JWT 认证（所有写接口）
- 密码 bcrypt 加密
- SQL 注入防护（SQLAlchemy ORM）
- CORS 配置

## 📊 性能

- RAG 查询耗时：< 5 秒（包含 LLM）
- 批量入库：1000 条/分钟
- 并发：支持 50 用户

## 🐛 故障排查

### Ollama 连接失败

```bash
# 检查 Ollama 是否运行
curl http://127.0.0.1:11434/api/version

# 检查模型是否拉取
ollama list
```

### FAISS 索引为空

```bash
# 检查索引文件
ls -lh storage/faiss_index/

# 手动入库测试数据
python -c "from apis.ingest import test_ingest; test_ingest()"
```

## 📄 许可

MIT License
