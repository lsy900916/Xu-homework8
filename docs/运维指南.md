# XU-News-AI-RAG 运维指南

**版本**: v1.0  
**创建日期**: 2026-6-30  
**运维负责人**: XU-News-AI-RAG Ops Team

---

## 1. 本地开发环境搭建

### 1.1 环境要求

**硬件要求**:

- CPU: 4 核及以上
- 内存: 8GB 及以上（Ollama 需要至少 4GB）
- 磁盘: 20GB 可用空间

**软件要求**:

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose（可选）
- Git

---

### 1.2 快速启动（一键脚本）

#### Windows

```bash
# 1. 克隆项目
git clone https://github.com/your-org/xu-news-ai-rag.git
cd xu-news-ai-rag

# 2. 运行初始化脚本
.\scripts\init.bat

# 3. 启动开发环境
.\scripts\dev.bat
```

#### Linux/Mac

```bash
# 1. 克隆项目
git clone https://github.com/your-org/xu-news-ai-rag.git
cd xu-news-ai-rag

# 2. 赋予脚本执行权限
chmod +x scripts/*.sh

# 3. 运行初始化脚本
./scripts/init.sh

# 4. 启动开发环境
./scripts/dev.sh
```

---

### 1.3 手动安装步骤

#### 1.3.1 安装 Ollama

**Windows**:

```bash
# 下载安装包
https://ollama.ai/download/windows

# 安装后验证
ollama --version
```

**Linux/Mac**:

```bash
# 使用官方安装脚本
curl -fsSL https://ollama.ai/install.sh | sh

# 验证
ollama --version
```

**拉取模型**:

```bash
# Embedding 模型（必需）
ollama pull mxbai-embed-large

# LLM 模型（二选一）
ollama pull qwen2.5:7b       # 中文优化，推荐
# 或
ollama pull llama3.1:8b      # 综合性能

# 验证模型
ollama list
```

---

#### 1.3.2 后端安装

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp ../.env.example .env
# 编辑 .env 文件，填入必要配置

# 初始化数据库
python manage.py init-db

# 创建管理员账户
python manage.py create-admin --email admin@xu-news.com --password Admin123

# 启动后端服务
python run.py
```

**验证**:

```bash
# 访问 http://localhost:5000/api/v1/system/health
curl http://localhost:5000/api/v1/system/health
```

---

#### 1.3.3 前端安装

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.local
# 编辑 .env.local，设置 VITE_API_BASE_URL=http://localhost:5000

# 启动前端服务
npm run dev
```

**访问**: http://localhost:3000

---

#### 1.3.4 n8n 安装

**Docker 方式（推荐）**:

```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**NPX 方式**:

```bash
npx n8n
```

**访问**: http://localhost:5678

**导入工作流**:

1. 登录 n8n
2. 点击 "Import from File"
3. 选择 `workflows/news_crawler_workflow.json`
4. 配置凭据（Backend API Endpoint、API Key）
5. 激活工作流

---

## 2. 环境变量配置

### 2.1 顶层环境变量 (.env)

```bash
# ==================== 应用配置 ====================
APP_ENV=development  # development, production
APP_DEBUG=true
APP_PORT=5000

# ==================== JWT 配置 ====================
JWT_SECRET=your-super-secret-key-change-in-production-min-32-chars
JWT_EXPIRATION_HOURS=24

# ==================== 数据库配置 ====================
DATABASE_URL=sqlite:///data/xu_news.db
# 或 PostgreSQL: postgresql://user:password@localhost:5432/xu_news

# ==================== Ollama 配置 ====================
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large
OLLAMA_LLM_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=60

# ==================== FAISS 配置 ====================
FAISS_INDEX_PATH=data/faiss_indexes/news_vectors.index
FAISS_INDEX_TYPE=IndexFlatL2  # IndexFlatL2, IndexIVFFlat
FAISS_DIMENSION=1024

# ==================== 爬虫配置 ====================
CRAWLER_USER_AGENT=XU-News-Bot/1.0 (+https://xu-news.com/bot; contact@xu-news.com)
CRAWLER_RATE_LIMIT=2  # 秒
CRAWLER_RESPECT_ROBOTS_TXT=true

# ==================== 百度搜索 API（可选）====================
BAIDU_API_KEY=your-baidu-api-key
BAIDU_SECRET_KEY=your-baidu-secret-key

# ==================== Redis 配置（可选）====================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# ==================== 邮件配置（可选）====================
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@xu-news.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=noreply@xu-news.com

# ==================== 日志配置 ====================
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_DIR=logs
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=30

# ==================== 安全配置 ====================
MAX_FAILED_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
PASSWORD_MIN_LENGTH=8
RATE_LIMIT_PER_MINUTE=100

# ==================== n8n API Key ====================
N8N_API_KEY=your-n8n-api-key-for-callback
```

### 2.2 前端环境变量 (frontend/.env.local)

```bash
# API 地址
VITE_API_BASE_URL=http://localhost:5000

# 应用配置
VITE_APP_TITLE=XU-News-AI-RAG
VITE_APP_VERSION=1.0.0

# 分页配置
VITE_PAGE_SIZE=20
```

---

## 3. 日志管理

### 3.1 日志目录结构

```
logs/
├── app.log              # 应用主日志
├── crawler.log          # 爬虫日志
├── rag.log              # RAG 问答日志
├── error.log            # 错误日志
├── access.log           # API 访问日志
└── security.log         # 安全事件日志
```

### 3.2 日志级别

- **DEBUG**: 详细调试信息（仅开发环境）
- **INFO**: 常规操作（用户登录、新闻入库、查询）
- **WARNING**: 警告信息（检索质量不足、回退搜索触发）
- **ERROR**: 错误信息（API 调用失败、数据库异常）
- **CRITICAL**: 严重错误（服务崩溃）

### 3.3 日志查看

**实时查看**:

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 查看爬虫日志
tail -f logs/crawler.log
```

**按时间过滤**:

```bash
# 查看今天的日志
grep "2026-6-30" logs/app.log

# 查看最近 1 小时的错误
grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" logs/error.log
```

**按关键词过滤**:

```bash
# 查看所有 ERROR 级别日志
grep "ERROR" logs/app.log

# 查看用户登录日志
grep "User login" logs/app.log
```

### 3.4 日志归档

**手动归档**:

```bash
# 压缩旧日志
tar -czf logs/archive/app_$(date +%Y%m%d).tar.gz logs/app.log
> logs/app.log  # 清空日志文件
```

**自动归档（logrotate）**:

```bash
# /etc/logrotate.d/xu-news
/var/log/xu-news/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload xu-news-backend
    endscript
}
```

---

## 4. 数据库管理

### 4.1 数据库备份

**手动备份**:

```bash
# SQLite 备份
cp backend/data/xu_news.db backend/data/backup/xu_news_$(date +%Y%m%d).db

# FAISS 索引备份
cp backend/data/faiss_indexes/news_vectors.index \
   backend/data/faiss_indexes/backup/news_vectors_$(date +%Y%m%d).index
```

**自动备份脚本**:

```bash
#!/bin/bash
# scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$DATE"

mkdir -p $BACKUP_DIR

# 备份数据库
cp backend/data/xu_news.db $BACKUP_DIR/

# 备份 FAISS 索引
cp -r backend/data/faiss_indexes $BACKUP_DIR/

# 压缩
tar -czf backups/xu_news_$DATE.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# 清理 7 天前的备份
find backups -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: xu_news_$DATE.tar.gz"
```

**定时备份（crontab）**:

```bash
# 每天凌晨 2 点备份
0 2 * * * /path/to/xu-news-ai-rag/scripts/backup.sh
```

---

### 4.2 数据库恢复

```bash
# 1. 停止服务
docker-compose down
# 或
systemctl stop xu-news-backend

# 2. 解压备份
tar -xzf backups/xu_news_20251009_020000.tar.gz

# 3. 恢复数据库
cp xu_news_20251009_020000/xu_news.db backend/data/

# 4. 恢复 FAISS 索引
cp -r xu_news_20251009_020000/faiss_indexes backend/data/

# 5. 启动服务
docker-compose up -d
# 或
systemctl start xu-news-backend
```

---

### 4.3 数据库迁移

**创建迁移**:

```bash
cd backend
python manage.py db migrate -m "Add column: category to news table"
```

**应用迁移**:

```bash
python manage.py db upgrade
```

**回滚迁移**:

```bash
python manage.py db downgrade
```

---

## 5. 服务管理

### 5.1 Docker Compose 方式（推荐）

**启动所有服务**:

```bash
docker-compose up -d
```

**查看服务状态**:

```bash
docker-compose ps
```

**查看日志**:

```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f backend
docker-compose logs -f frontend
```

**重启服务**:

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

**停止服务**:

```bash
docker-compose down
```

**重建服务**:

```bash
# 重新构建镜像
docker-compose build

# 重建并启动
docker-compose up -d --build
```

---

### 5.2 Systemd 方式（生产环境）

**后端服务配置** (`/etc/systemd/system/xu-news-backend.service`):

```ini
[Unit]
Description=XU-News AI-RAG Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/xu-news-ai-rag/backend
Environment="PATH=/opt/xu-news-ai-rag/backend/venv/bin"
ExecStart=/opt/xu-news-ai-rag/backend/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**启动服务**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable xu-news-backend
sudo systemctl start xu-news-backend
```

**查看状态**:

```bash
sudo systemctl status xu-news-backend
```

**查看日志**:

```bash
sudo journalctl -u xu-news-backend -f
```

---

## 6. 性能监控

### 6.1 系统资源监控

**CPU & 内存**:

```bash
# 实时监控
htop

# Docker 容器资源
docker stats
```

**磁盘空间**:

```bash
# 查看磁盘使用
df -h

# 查看目录大小
du -sh backend/data/*
```

---

### 6.2 应用监控

**健康检查**:

```bash
curl http://localhost:5000/api/v1/system/health
```

**响应示例**:

```json
{
  "status": "healthy",
  "timestamp": "2026-6-30T10:30:00Z",
  "services": {
    "database": { "status": "up", "response_time_ms": 5 },
    "faiss": { "status": "up", "total_vectors": 15000 },
    "ollama": { "status": "up", "models": ["qwen2.5:7b", "mxbai-embed-large"] },
    "redis": { "status": "up" }
  }
}
```

**API 性能监控**:

```bash
# 使用 Apache Bench
ab -n 100 -c 10 http://localhost:5000/api/v1/news

# 使用 wrk
wrk -t4 -c100 -d30s http://localhost:5000/api/v1/news
```

---

### 6.3 数据库性能

**SQLite 性能分析**:

```bash
# 进入数据库
sqlite3 backend/data/xu_news.db

# 查看表大小
.schema news

# 分析查询性能
EXPLAIN QUERY PLAN SELECT * FROM news WHERE published_at > '2025-10-01';

# 重建索引
REINDEX;

# 清理碎片
VACUUM;
```

---

## 7. 常见问题排查

### 7.1 后端无法启动

**问题**: `ModuleNotFoundError: No module named 'flask'`

**解决**:

```bash
# 确认虚拟环境已激活
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 重新安装依赖
pip install -r requirements.txt
```

---

**问题**: `OperationalError: unable to open database file`

**解决**:

```bash
# 检查数据库目录是否存在
mkdir -p backend/data

# 检查权限
chmod 755 backend/data
```

---

### 7.2 Ollama 连接失败

**问题**: `ConnectionError: [Errno 111] Connection refused`

**解决**:

```bash
# 检查 Ollama 是否运行
curl http://127.0.0.1:11434/api/version

# 启动 Ollama（如果未运行）
ollama serve

# 检查环境变量
echo $OLLAMA_HOST
```

---

### 7.3 FAISS 索引损坏

**问题**: `RuntimeError: Invalid index file`

**解决**:

```bash
# 从备份恢复
cp backend/data/faiss_indexes/backup/news_vectors_20251009.index \
   backend/data/faiss_indexes/news_vectors.index

# 或重建索引
python manage.py rebuild-faiss-index
```

---

### 7.4 前端 API 调用失败

**问题**: `Network Error` / `CORS Error`

**解决**:

```bash
# 检查后端是否运行
curl http://localhost:5000/api/v1/system/health

# 检查前端 .env.local 配置
cat frontend/.env.local
# 确认 VITE_API_BASE_URL=http://localhost:5000

# 检查浏览器控制台是否有 CORS 错误
# 如果有，检查后端 CORS 配置
```

---

### 7.5 n8n 工作流执行失败

**问题**: 工作流显示错误

**排查步骤**:

1. 查看 n8n 执行日志
2. 检查 Backend API Endpoint 配置（应为 `http://backend:5000` 或 `http://localhost:5000`）
3. 检查 API Key 是否正确
4. 测试 API 是否可访问：
   ```bash
   curl -X POST http://localhost:5000/api/v1/news/ingest \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"title": "Test", "content": "..."}'
   ```

---

### 7.6 RAG 检索质量差

**问题**: 返回的新闻不相关

**排查**:

1. 检查 FAISS 索引数量：

   ```bash
   curl http://localhost:5000/api/v1/system/stats
   # 查看 total_vectors
   ```

2. 检查 Embedding 模型：

   ```bash
   ollama list
   # 确认 mxbai-embed-large 已安装
   ```

3. 增加检索数量（`top_k`）：

   ```json
   {
     "question": "...",
     "top_k": 10 // 增加到 10
   }
   ```

4. 启用回退搜索：
   ```json
   {
     "question": "...",
     "enable_fallback": true
   }
   ```

---

## 8. 性能优化建议

### 8.1 数据库优化

**SQLite 优化**:

```python
# backend/app/config/config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "connect_args": {
        "check_same_thread": False,
        "timeout": 15
    }
}
```

**定期维护**:

```bash
# 每周执行一次
sqlite3 backend/data/xu_news.db "VACUUM;"
sqlite3 backend/data/xu_news.db "ANALYZE;"
```

---

### 8.2 FAISS 优化

**使用 IVF 索引（数据量 > 10 万）**:

```python
# 迁移到 IVF 索引
python manage.py migrate-faiss-to-ivf --nlist 100
```

**GPU 加速（可选）**:

```python
# 需要 CUDA 环境
pip install faiss-gpu
```

---

### 8.3 缓存优化

**启用 Redis 缓存**:

```bash
# 安装 Redis
docker run -d --name redis -p 6379:6379 redis:alpine

# 配置 .env
REDIS_HOST=localhost
REDIS_PORT=6379
```

**缓存策略**:

- RAG 问答结果: 1 小时
- 关键词统计: 30 分钟
- 新闻列表: 5 分钟

---

## 9. 安全运维

### 9.1 定期安全检查

```bash
# 检查依赖漏洞
cd backend
pip-audit

cd ../frontend
npm audit

# 检查密钥强度
python -c "import os; print('JWT_SECRET 长度:', len(os.getenv('JWT_SECRET')))"
# 应 >= 32
```

### 9.2 更新依赖

```bash
# 后端
cd backend
pip list --outdated
pip install --upgrade <package>

# 前端
cd frontend
npm outdated
npm update
```

### 9.3 日志审计

```bash
# 查看登录失败记录
grep "login failed" logs/security.log

# 查看账户锁定记录
grep "account locked" logs/security.log

# 查看速率限制触发
grep "rate limit exceeded" logs/app.log
```

---

## 10. 升级指南

### 10.1 备份数据

```bash
# 执行备份脚本
./scripts/backup.sh
```

### 10.2 停止服务

```bash
docker-compose down
# 或
systemctl stop xu-news-backend
systemctl stop xu-news-frontend
```

### 10.3 更新代码

```bash
git pull origin main
```

### 10.4 更新依赖

```bash
# 后端
cd backend
pip install -r requirements.txt --upgrade

# 前端
cd ../frontend
npm install
```

### 10.5 数据库迁移

```bash
cd backend
python manage.py db upgrade
```

### 10.6 重启服务

```bash
docker-compose up -d --build
# 或
systemctl start xu-news-backend
systemctl start xu-news-frontend
```

### 10.7 验证

```bash
# 健康检查
curl http://localhost:5000/api/v1/system/health

# 访问前端
open http://localhost:3000
```

---

## 11. 故障恢复

### 11.1 灾难恢复流程

1. **评估损坏范围**
2. **恢复备份数据**（数据库 + FAISS 索引）
3. **重建服务**（重新拉取镜像/重新安装依赖）
4. **验证数据完整性**
5. **恢复服务**
6. **通知用户**

### 11.2 回滚版本

```bash
# 查看 Git 历史
git log --oneline

# 回滚到指定版本
git checkout <commit-hash>

# 重启服务
docker-compose up -d --build
```

---

## 12. 联系与支持

**技术支持**:

- 邮箱: support@xu-news.com
- 文档: https://docs.xu-news.com
- GitHub Issues: https://github.com/your-org/xu-news-ai-rag/issues

**紧急联系**:

- 电话: +86 xxx-xxxx-xxxx
- 值班工程师: oncall@xu-news.com

---

**文档状态**: ✅ 已评审  
**最后更新**: 2026-6-30
