# XU-News-AI-RAG 数据设计文档

**版本**: v1.0  
**创建日期**: 2026-6-30  
**数据架构师**: XU-News-AI-RAG Team

---

## 1. 数据存储概述

XU-News-AI-RAG 采用混合存储架构：

- **SQLite**: 存储结构化数据（用户、新闻元数据、历史记录）
- **FAISS**: 存储新闻内容向量（用于相似度检索）
- **Redis**: 缓存热点数据（可选）

### 1.1 存储分层架构

```mermaid
graph TB
    subgraph "应用层"
        A[Flask API]
    end

    subgraph "缓存层"
        B[Redis]
    end

    subgraph "持久化层"
        C[(SQLite)]
        D[FAISS Index Files]
    end

    A --> B
    A --> C
    A --> D
    B -.过期.-> C
```

---

## 2. SQLite 数据库设计

### 2.1 数据库配置

**文件路径**: `backend/data/xu_news.db`

**配置参数**:

```python
# SQLAlchemy 配置
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/xu_news.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # 生产环境关闭 SQL 日志
```

**优化设置**:

```sql
-- 启用 WAL 模式（提升并发读写）
PRAGMA journal_mode=WAL;

-- 设置缓存大小（10MB）
PRAGMA cache_size=-10000;

-- 启用外键约束
PRAGMA foreign_keys=ON;
```

---

### 2.2 表结构设计

#### 2.2.1 用户表 (users)

**用途**: 存储用户账户信息

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100),
    avatar_url VARCHAR(500),
    role VARCHAR(20) DEFAULT 'user',  -- user, admin
    is_active BOOLEAN DEFAULT 1,
    is_locked BOOLEAN DEFAULT 0,
    failed_login_attempts INTEGER DEFAULT 0,
    last_login_at DATETIME,
    locked_until DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    CONSTRAINT chk_email CHECK (email LIKE '%@%'),
    CONSTRAINT chk_role CHECK (role IN ('user', 'admin'))
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);
```

**字段说明**:
| 字段 | 类型 | 约束 | 说明 |
|-----|------|-----|------|
| id | INTEGER | PK, AUTO_INCREMENT | 用户唯一标识 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 登录邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 加密后的密码 |
| username | VARCHAR(100) | - | 用户昵称 |
| avatar_url | VARCHAR(500) | - | 头像 URL |
| role | VARCHAR(20) | DEFAULT 'user' | 用户角色 |
| is_active | BOOLEAN | DEFAULT 1 | 账户是否激活 |
| is_locked | BOOLEAN | DEFAULT 0 | 是否锁定 |
| failed_login_attempts | INTEGER | DEFAULT 0 | 连续登录失败次数 |
| locked_until | DATETIME | - | 锁定截止时间 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | DEFAULT NOW | 更新时间 |

**示例数据**:

```sql
INSERT INTO users (email, password_hash, username, role) VALUES
('admin@xu-news.com', '$2b$12$...', 'Admin', 'admin'),
('user1@example.com', '$2b$12$...', 'User1', 'user');
```

---

#### 2.2.2 新闻表 (news)

**用途**: 存储新闻元数据

```sql
CREATE TABLE news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    url VARCHAR(1000) NOT NULL UNIQUE,
    url_hash VARCHAR(64) NOT NULL,  -- MD5/SHA256 哈希
    source VARCHAR(200),            -- 新闻来源（如"新华网"）
    author VARCHAR(100),
    published_at DATETIME,          -- 新闻发布时间
    crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 爬取时间

    -- 向量索引相关
    vector_indexed BOOLEAN DEFAULT 0,
    faiss_id INTEGER,                -- FAISS 索引中的 ID（与本表 id 一致）
    embedding_model VARCHAR(100),    -- 使用的 Embedding 模型

    -- 分类与标签
    category VARCHAR(100),           -- 新闻分类（科技/财经/体育...）
    tags TEXT,                       -- JSON 数组，如 '["AI", "科技"]'

    -- 统计字段
    view_count INTEGER DEFAULT 0,
    reference_count INTEGER DEFAULT 0,  -- 被 RAG 引用次数

    -- 软删除
    is_deleted BOOLEAN DEFAULT 0,
    deleted_at DATETIME,

    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CONSTRAINT chk_url_hash CHECK (LENGTH(url_hash) IN (32, 64))
);

-- 索引
CREATE UNIQUE INDEX idx_news_url ON news(url);
CREATE INDEX idx_news_url_hash ON news(url_hash);
CREATE INDEX idx_news_published_at ON news(published_at DESC);
CREATE INDEX idx_news_vector_indexed ON news(vector_indexed);
CREATE INDEX idx_news_category ON news(category);
CREATE INDEX idx_news_is_deleted ON news(is_deleted);
CREATE INDEX idx_news_crawled_at ON news(crawled_at DESC);

-- 全文搜索索引（SQLite FTS5）
CREATE VIRTUAL TABLE news_fts USING fts5(
    title,
    content,
    content='news',
    content_rowid='id'
);
```

**字段说明**:
| 字段 | 类型 | 约束 | 说明 |
|-----|------|-----|------|
| id | INTEGER | PK, AUTO_INCREMENT | 新闻唯一标识（与 FAISS ID 对应） |
| title | VARCHAR(500) | NOT NULL | 新闻标题 |
| content | TEXT | NOT NULL | 新闻正文（纯文本） |
| summary | TEXT | - | 新闻摘要（可由 LLM 生成） |
| url | VARCHAR(1000) | UNIQUE, NOT NULL | 原始 URL |
| url_hash | VARCHAR(64) | NOT NULL | URL 哈希（去重） |
| source | VARCHAR(200) | - | 新闻来源 |
| published_at | DATETIME | - | 新闻发布时间 |
| vector_indexed | BOOLEAN | DEFAULT 0 | 是否已向量化 |
| faiss_id | INTEGER | - | FAISS 索引 ID |
| embedding_model | VARCHAR(100) | - | Embedding 模型名称 |
| category | VARCHAR(100) | - | 新闻分类 |
| reference_count | INTEGER | DEFAULT 0 | RAG 引用次数 |
| is_deleted | BOOLEAN | DEFAULT 0 | 软删除标记 |

**示例数据**:

```sql
INSERT INTO news (title, content, url, url_hash, source, published_at) VALUES
(
    'OpenAI发布GPT-5模型',
    'OpenAI今日宣布发布最新一代语言模型GPT-5...',
    'https://example.com/news/gpt5',
    'a1b2c3d4e5f6...',
    '科技日报',
    '2026-6-30 10:00:00'
);
```

---

#### 2.2.3 问答历史表 (query_history)

**用途**: 记录用户 RAG 问答记录

```sql
CREATE TABLE query_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT,

    -- RAG 检索信息
    retrieved_news_ids TEXT,        -- JSON 数组，如 '[1, 5, 10]'
    retrieval_scores TEXT,          -- JSON 数组，检索得分
    retrieval_method VARCHAR(50),   -- 'faiss', 'baidu', 'hybrid'

    -- LLM 信息
    llm_model VARCHAR(100),
    llm_tokens_used INTEGER,
    llm_response_time FLOAT,        -- 秒

    -- 用户反馈
    user_feedback VARCHAR(20),      -- 'positive', 'negative', null
    feedback_comment TEXT,

    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- 外键
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_query_history_user_id ON query_history(user_id);
CREATE INDEX idx_query_history_created_at ON query_history(created_at DESC);
CREATE INDEX idx_query_history_feedback ON query_history(user_feedback);
```

**字段说明**:
| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户 ID |
| question | TEXT | 用户提问 |
| answer | TEXT | 系统回答 |
| retrieved_news_ids | TEXT | 检索到的新闻 ID（JSON） |
| retrieval_method | VARCHAR(50) | 检索方式 |
| llm_model | VARCHAR(100) | 使用的 LLM 模型 |
| user_feedback | VARCHAR(20) | 用户反馈（好评/差评） |

---

#### 2.2.4 新闻源配置表 (news_sources)

**用途**: 管理爬虫新闻源

```sql
CREATE TABLE news_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    category VARCHAR(100),

    -- 爬虫配置
    crawl_enabled BOOLEAN DEFAULT 1,
    crawl_interval INTEGER DEFAULT 3600,  -- 秒
    last_crawl_at DATETIME,
    next_crawl_at DATETIME,

    -- 选择器配置（JSON）
    selectors TEXT,  -- {"title": ".article-title", "content": ".article-body"}

    -- 统计
    total_crawled INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    fail_count INTEGER DEFAULT 0,

    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_news_sources_enabled ON news_sources(crawl_enabled);
CREATE INDEX idx_news_sources_next_crawl ON news_sources(next_crawl_at);
```

---

#### 2.2.5 聚类结果表 (cluster_results)

**用途**: 存储聚类分析结果

```sql
CREATE TABLE cluster_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- 聚类参数
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    n_clusters INTEGER NOT NULL,
    algorithm VARCHAR(50),          -- 'kmeans', 'dbscan'

    -- 聚类结果（JSON）
    clusters TEXT,                  -- [{"cluster_id": 0, "news_ids": [1,2,3], "topic": "AI发展"}]
    visualization_data TEXT,        -- t-SNE 降维后的 2D 坐标

    -- 统计
    total_news_count INTEGER,
    silhouette_score FLOAT,         -- 聚类质量评分

    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_cluster_results_date_range ON cluster_results(start_date, end_date);
```

---

#### 2.2.6 关键词统计表 (keyword_stats)

**用途**: 缓存关键词统计结果

```sql
CREATE TABLE keyword_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- 统计维度
    time_range VARCHAR(50),         -- 'daily', 'weekly', 'monthly'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    category VARCHAR(100),          -- 可选：分类筛选

    -- 关键词结果（JSON）
    keywords TEXT,                  -- [{"word": "AI", "count": 150}, ...]

    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME             -- 缓存过期时间
);

-- 索引
CREATE INDEX idx_keyword_stats_range ON keyword_stats(time_range, start_date, end_date);
CREATE INDEX idx_keyword_stats_expires ON keyword_stats(expires_at);
```

---

### 2.3 数据关系图

```mermaid
erDiagram
    users ||--o{ query_history : "1:N"
    news ||--o{ query_history : "N:M (via retrieved_news_ids)"
    news_sources ||--o{ news : "1:N"

    users {
        int id PK
        string email UK
        string password_hash
        string role
        datetime created_at
    }

    news {
        int id PK
        string title
        text content
        string url UK
        string url_hash
        int faiss_id
        datetime published_at
        boolean vector_indexed
    }

    query_history {
        int id PK
        int user_id FK
        text question
        text answer
        text retrieved_news_ids
        datetime created_at
    }

    news_sources {
        int id PK
        string name
        string base_url
        boolean crawl_enabled
        int crawl_interval
    }

    cluster_results {
        int id PK
        date start_date
        date end_date
        text clusters
        datetime created_at
    }

    keyword_stats {
        int id PK
        string time_range
        text keywords
        datetime expires_at
    }
```

---

## 3. FAISS 向量索引设计

### 3.1 索引结构

**索引类型**: `IndexFlatL2` (精确检索) 或 `IndexIVFFlat` (大规模数据)

**向量维度**: 1024（取决于 Embedding 模型）

**文件路径**: `backend/data/faiss_indexes/news_vectors.index`

### 3.2 索引-元数据映射

**核心原则**: FAISS 索引 ID 与 SQLite `news.id` 严格一致

```python
# 添加向量时
news_id = 123  # SQLite 中的新闻 ID
vector = embedding_model.embed_query(news.content)

# 确保 FAISS ID = news_id
faiss_index.add_with_ids(
    np.array([vector], dtype='float32'),
    np.array([news_id], dtype='int64')
)

# 更新 SQLite
news.faiss_id = news_id
news.vector_indexed = True
db.commit()
```

### 3.3 FAISS 索引文件结构

```
backend/data/faiss_indexes/
├── news_vectors.index       # 主索引文件
├── news_vectors.index.meta  # 元数据（模型名、向量维度、创建时间）
└── backup/
    └── news_vectors_20251009.index  # 定期备份
```

**元数据文件示例 (JSON)**:

```json
{
  "index_type": "IndexFlatL2",
  "dimension": 1024,
  "total_vectors": 15000,
  "embedding_model": "mxbai-embed-large",
  "created_at": "2026-6-30T10:00:00Z",
  "last_updated_at": "2026-6-30T18:30:00Z"
}
```

### 3.4 检索流程数据流

```mermaid
sequenceDiagram
    participant API as Flask API
    participant EMB as Embedding Model
    participant FAISS as FAISS Index
    participant DB as SQLite

    API->>EMB: embed_query("用户问题")
    EMB-->>API: query_vector (1024-dim)
    API->>FAISS: search(query_vector, k=5)
    FAISS-->>API: [indices=[123,456,...], distances=[0.2,0.5,...]]
    API->>DB: SELECT * FROM news WHERE id IN (123,456,...)
    DB-->>API: news_list
    API->>API: 构建响应 {news, scores}
```

---

## 4. Redis 缓存设计（可选）

### 4.1 缓存键命名规范

**格式**: `xu_news:{namespace}:{key}`

**示例**:

```
xu_news:rag_query:hash_of_question        # RAG 问答缓存
xu_news:keyword_stats:daily:2026-6-30    # 关键词统计缓存
xu_news:news_detail:123                   # 新闻详情缓存
xu_news:user_token:user_456               # 用户 Token 黑名单
```

### 4.2 缓存策略

| 数据类型     | TTL           | 说明           |
| ------------ | ------------- | -------------- |
| RAG 问答结果 | 3600s (1h)    | 相同问题复用   |
| 关键词统计   | 1800s (30min) | 高频访问       |
| 新闻详情     | 300s (5min)   | 减轻数据库压力 |
| 热门新闻列表 | 600s (10min)  | 首页展示       |

### 4.3 缓存数据结构

**RAG 问答缓存**:

```python
# 键
cache_key = f"xu_news:rag_query:{hashlib.md5(question.encode()).hexdigest()}"

# 值（JSON）
{
    "question": "最近关于AI的新闻有哪些？",
    "answer": "根据检索到的新闻...",
    "news_ids": [123, 456, 789],
    "cached_at": "2026-6-30T10:30:00Z"
}
```

---

## 5. 数据一致性保证

### 5.1 SQLite 与 FAISS 同步机制

**原子性操作**:

```python
def ingest_news(news_data):
    try:
        # 1. 开启数据库事务
        db.session.begin()

        # 2. 插入 SQLite
        news = News(**news_data)
        db.session.add(news)
        db.session.flush()  # 获取自增 ID

        # 3. 生成向量
        vector = embedding_model.embed_query(news.content)

        # 4. 添加到 FAISS（使用 SQLite ID）
        faiss_index.add_with_ids(
            np.array([vector], dtype='float32'),
            np.array([news.id], dtype='int64')
        )

        # 5. 更新 SQLite 索引状态
        news.faiss_id = news.id
        news.vector_indexed = True

        # 6. 提交事务
        db.session.commit()

        # 7. 持久化 FAISS 索引
        faiss.write_index(faiss_index, "news_vectors.index")

    except Exception as e:
        db.session.rollback()
        logger.error(f"入库失败: {e}")
        raise
```

### 5.2 定期同步检查

**定时任务（每天凌晨 2 点）**:

```python
def sync_check():
    # 查找未索引的新闻
    unindexed = News.query.filter_by(vector_indexed=False).all()

    for news in unindexed:
        try:
            # 补索引
            vector = embedding_model.embed_query(news.content)
            faiss_index.add_with_ids(
                np.array([vector], dtype='float32'),
                np.array([news.id], dtype='int64')
            )
            news.vector_indexed = True
            db.session.commit()
        except Exception as e:
            logger.error(f"补索引失败 news_id={news.id}: {e}")
```

---

## 6. 数据备份与恢复

### 6.1 备份策略

**每日备份**:

```bash
#!/bin/bash
# 备份 SQLite
DATE=$(date +%Y%m%d)
cp backend/data/xu_news.db backend/data/backup/xu_news_$DATE.db

# 备份 FAISS 索引
cp backend/data/faiss_indexes/news_vectors.index \
   backend/data/faiss_indexes/backup/news_vectors_$DATE.index

# 只保留最近 7 天
find backend/data/backup -name "*.db" -mtime +7 -delete
find backend/data/faiss_indexes/backup -name "*.index" -mtime +7 -delete
```

### 6.2 恢复流程

**从备份恢复**:

```bash
# 停止服务
docker-compose down

# 恢复数据库
cp backend/data/backup/xu_news_20251009.db backend/data/xu_news.db

# 恢复 FAISS 索引
cp backend/data/faiss_indexes/backup/news_vectors_20251009.index \
   backend/data/faiss_indexes/news_vectors.index

# 启动服务
docker-compose up -d
```

---

## 7. 数据迁移与扩展

### 7.1 从 SQLite 迁移到 PostgreSQL

**迁移步骤**:

```python
# 1. 导出 SQLite 数据
sqlite_engine = create_engine('sqlite:///xu_news.db')
df = pd.read_sql("SELECT * FROM news", sqlite_engine)

# 2. 导入 PostgreSQL
pg_engine = create_engine('postgresql://user:pass@localhost/xu_news')
df.to_sql('news', pg_engine, if_exists='append', index=False)

# 3. 重建索引
with pg_engine.connect() as conn:
    conn.execute("CREATE INDEX idx_news_published_at ON news(published_at DESC)")
```

### 7.2 FAISS 索引扩容

**从 Flat 迁移到 IVF**:

```python
import faiss

# 1. 读取现有索引
index_flat = faiss.read_index("news_vectors.index")

# 2. 创建 IVF 索引
quantizer = faiss.IndexFlatL2(1024)
index_ivf = faiss.IndexIVFFlat(quantizer, 1024, 100)  # 100 个聚类中心

# 3. 训练索引
vectors = index_flat.reconstruct_n(0, index_flat.ntotal)
index_ivf.train(vectors)

# 4. 添加向量
index_ivf.add(vectors)

# 5. 保存新索引
faiss.write_index(index_ivf, "news_vectors_ivf.index")
```

---

## 8. 数据安全与隐私

### 8.1 敏感数据处理

**密码存储**:

```python
from passlib.hash import bcrypt

# 存储
password_hash = bcrypt.hash(plain_password, rounds=12)

# 验证
is_valid = bcrypt.verify(plain_password, password_hash)
```

**邮箱脱敏**:

```python
def mask_email(email):
    # user@example.com -> u***@example.com
    local, domain = email.split('@')
    return f"{local[0]}***@{domain}"
```

### 8.2 数据清理

**定期删除过期数据**:

```sql
-- 删除 90 天前的问答历史
DELETE FROM query_history
WHERE created_at < datetime('now', '-90 days');

-- 删除软删除超过 30 天的新闻
DELETE FROM news
WHERE is_deleted = 1
  AND deleted_at < datetime('now', '-30 days');
```

---

## 9. 性能优化建议

### 9.1 数据库优化

**批量插入**:

```python
# 不推荐（逐条插入）
for news_data in news_list:
    news = News(**news_data)
    db.session.add(news)
    db.session.commit()  # 每次都提交

# 推荐（批量提交）
for news_data in news_list:
    news = News(**news_data)
    db.session.add(news)
db.session.commit()  # 一次提交
```

**分页查询**:

```python
# 使用 LIMIT OFFSET
news_list = News.query.order_by(
    News.published_at.desc()
).limit(20).offset(page * 20).all()
```

### 9.2 FAISS 优化

**使用 GPU 加速（可选）**:

```python
import faiss

# CPU 索引
index_cpu = faiss.IndexFlatL2(1024)

# 转换为 GPU 索引
res = faiss.StandardGpuResources()
index_gpu = faiss.index_cpu_to_gpu(res, 0, index_cpu)
```

---

## 10. 监控指标

### 10.1 数据库监控

```python
@app.route('/metrics/database')
def database_metrics():
    return {
        "total_news": News.query.count(),
        "indexed_news": News.query.filter_by(vector_indexed=True).count(),
        "total_users": User.query.count(),
        "total_queries": QueryHistory.query.count(),
        "db_size_mb": os.path.getsize("data/xu_news.db") / 1024 / 1024
    }
```

### 10.2 FAISS 监控

```python
@app.route('/metrics/faiss')
def faiss_metrics():
    return {
        "total_vectors": faiss_index.ntotal,
        "index_type": type(faiss_index).__name__,
        "dimension": faiss_index.d,
        "index_size_mb": os.path.getsize("faiss_indexes/news_vectors.index") / 1024 / 1024
    }
```

---

**文档状态**: ✅ 已评审  
**最后更新**: 2026-6-30
