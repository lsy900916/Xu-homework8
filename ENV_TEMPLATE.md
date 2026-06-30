# 环境变量配置模板

请将以下内容保存为 `.env` 文件：

```bash
# ======================================================================
# XU-News-AI-RAG 环境变量配置模板
# ======================================================================

# ==================== 应用基础配置 ====================
APP_ENV=development
APP_DEBUG=true
APP_PORT=5000
APP_DOMAIN=localhost

# ==================== JWT 认证配置 ====================
# 生产环境必须修改！
JWT_SECRET=your-super-secret-key-change-in-production-min-32-chars
JWT_EXPIRATION_HOURS=24
JWT_ALGORITHM=HS256

# ==================== 数据库配置 ====================
DATABASE_URL=sqlite:///data/xu_news.db

# ==================== Ollama 配置 ====================
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large
OLLAMA_LLM_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=60

# ==================== FAISS 配置 ====================
FAISS_INDEX_PATH=data/faiss_indexes/news_vectors.index
FAISS_INDEX_TYPE=IndexFlatL2
FAISS_DIMENSION=1024

# ==================== 爬虫配置 ====================
CRAWLER_USER_AGENT=XU-News-Bot/1.0 (+https://xu-news.com/bot; contact@xu-news.com)
CRAWLER_RATE_LIMIT=2
CRAWLER_RESPECT_ROBOTS_TXT=true

# ==================== 百度搜索 API（可选）====================
BAIDU_API_KEY=
BAIDU_SECRET_KEY=

# ==================== Redis 配置（可选）====================
REDIS_ENABLED=false
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# ==================== 邮件配置（可选）====================
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@xu-news.com
SMTP_PASSWORD=
SMTP_FROM=noreply@xu-news.com
ALERT_EMAIL=admin@xu-news.com

# ==================== 日志配置 ====================
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=30

# ==================== 安全配置 ====================
MAX_FAILED_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
PASSWORD_MIN_LENGTH=8
RATE_LIMIT_PER_MINUTE=100

# ==================== n8n 配置 ====================
N8N_API_KEY=your-n8n-api-key-for-callback
```

详细说明见 [OPS_GUIDE.md](docs/OPS_GUIDE.md)

