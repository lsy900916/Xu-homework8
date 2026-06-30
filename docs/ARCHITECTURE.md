# XU-News-AI-RAG 系统架构文档

**版本**: v1.0  
**创建日期**: 2026-6-30  
**架构师**: XU-News-AI-RAG Team

---

## 1. 架构概述

XU-News-AI-RAG 采用前后端分离的 Monorepo 架构，结合工作流自动化、向量检索、大语言模型，构建智能新闻检索与问答系统。

### 1.1 设计原则

- **模块化**: 各模块职责清晰，松耦合
- **可扩展**: 支持水平扩展与功能扩展
- **高性能**: 向量检索 + 缓存机制
- **安全性**: 认证鉴权 + 数据加密
- **可观测**: 日志、监控、追踪

---

## 2. 系统架构图

### 2.1 整体架构

```mermaid
graph TB
    subgraph "用户层"
        A[Web Browser]
    end

    subgraph "前端层"
        B[React + Vite]
    end

    subgraph "API网关层"
        C[Nginx]
    end

    subgraph "应用层"
        D[Flask API Server]
        E[n8n Workflow Engine]
    end

    subgraph "业务逻辑层"
        F[Auth Service]
        G[News Ingestion Service]
        H[RAG Service]
        I[Clustering Service]
        J[Keyword Service]
    end

    subgraph "AI层"
        K[Ollama LLM]
        L[Embedding Model]
        M[FAISS Vector Store]
    end

    subgraph "数据层"
        N[(SQLite DB)]
        O[FAISS Index Files]
        P[Redis Cache]
    end

    subgraph "外部服务"
        Q[百度搜索 API]
        R[新闻网站]
    end

    A --> B
    B --> C
    C --> D
    E --> D
    D --> F
    D --> G
    D --> H
    D --> I
    D --> J

    F --> N
    G --> N
    G --> L
    G --> M
    H --> M
    H --> K
    H --> Q
    I --> M
    J --> N

    E --> R

    M --> O
    D --> P
```

### 2.2 技术栈分层

```mermaid
graph LR
    subgraph "前端技术栈"
        FE1[React 18]
        FE2[TypeScript]
        FE3[TailwindCSS]
        FE4[Zustand]
        FE5[Axios]
    end

    subgraph "后端技术栈"
        BE1[Flask 3.x]
        BE2[LangChain]
        BE3[FAISS]
        BE4[SQLAlchemy]
        BE5[Celery]
        BE6[JWT]
    end

    subgraph "AI技术栈"
        AI1[Ollama]
        AI2[mxbai-embed-large]
        AI3[qwen2.5 / llama3.1]
    end

    subgraph "工具链"
        T1[n8n]
        T2[Docker]
        T3[Nginx]
    end
```

---

## 3. 模块职责详解

### 3.1 前端模块 (Frontend)

**技术**: React 18 + Vite + TypeScript

**职责**:

- 用户界面渲染
- 用户交互处理
- API 调用封装
- 状态管理
- 路由管理

**核心页面**:

```
/login          - 登录页
/register       - 注册页
/dashboard      - 仪表盘（数据概览）
/chat           - RAG 问答界面
/news           - 新闻列表与检索
/cluster        - 聚类分析可视化
/keywords       - 关键词统计
/history        - 历史记录
/settings       - 用户设置
```

**组件结构**:

```
/components
  /common       - 通用组件（Button, Input, Modal）
  /layout       - 布局组件（Header, Sidebar, Footer）
  /chat         - 聊天相关组件（MessageList, InputBox）
  /news         - 新闻相关组件（NewsCard, NewsFilter）
  /charts       - 图表组件（ClusterChart, KeywordCloud）
```

---

### 3.2 后端模块 (Backend)

**技术**: Flask + LangChain + FAISS + SQLite

#### 3.2.1 API Server

**职责**:

- RESTful API 提供
- 请求路由与参数验证
- 认证鉴权中间件
- 错误处理与日志

**目录结构**:

```
/app
  /api
    /v1
      auth.py           - 认证接口
      news.py           - 新闻管理接口
      rag.py            - RAG 问答接口
      cluster.py        - 聚类分析接口
      keyword.py        - 关键词统计接口
      history.py        - 历史记录接口
  /models
    user.py             - 用户模型
    news.py             - 新闻模型
    history.py          - 历史记录模型
  /services
    auth_service.py     - 认证业务逻辑
    news_service.py     - 新闻业务逻辑
    rag_service.py      - RAG 业务逻辑
    cluster_service.py  - 聚类业务逻辑
    keyword_service.py  - 关键词业务逻辑
  /rag
    embeddings.py       - Embedding 封装
    vector_store.py     - FAISS 封装
    llm_client.py       - Ollama 客户端
    retriever.py        - 检索器
    chain.py            - LangChain 链
  /utils
    validators.py       - 参数验证
    decorators.py       - 装饰器（认证、限流）
    logger.py           - 日志工具
  /config
    config.py           - 配置管理
```

#### 3.2.2 核心服务职责

##### Auth Service

- 用户注册（密码加密、邮箱验证）
- 用户登录（JWT Token 签发）
- Token 验证与刷新
- 密码重置
- 账户锁定机制

##### News Ingestion Service

- 接收 n8n 爬取的新闻数据
- 数据清洗与标准化
- 去重检测（URL Hash）
- 存储到 SQLite
- 调用 Embedding 生成向量
- 更新 FAISS 索引
- 返回入库状态

##### RAG Service

- 接收用户问题
- 调用 Embedding 模型向量化问题
- 在 FAISS 中检索 Top-K 相关新闻
- 评估检索质量（相似度阈值）
- 触发回退搜索（百度 API）
- 构建 LangChain Prompt
- 调用 Ollama 生成答案
- 格式化返回（答案 + 来源引用）
- 记录问答历史

##### Clustering Service

- 筛选指定时间范围的新闻
- 从 FAISS 读取向量
- 执行聚类算法（K-Means/DBSCAN）
- 主题标签生成（关键词提取或 LLM 总结）
- 生成可视化数据（t-SNE 降维）
- 导出报告

##### Keyword Service

- 时间维度筛选新闻
- 文本预处理（分词、去停用词）
- 关键词提取（TF-IDF/TextRank）
- 频次统计与排序
- 返回 Top10 关键词

---

### 3.3 工作流模块 (n8n)

**职责**:

- 定时任务调度
- HTTP 请求发起
- HTML 解析
- 数据转换
- API 回调

**工作流示例**:

#### Workflow 1: 新闻爬取

```mermaid
graph LR
    A[定时触发<br/>每小时] --> B[HTTP Request<br/>GET 新闻列表页]
    B --> C[HTML Extract<br/>提取新闻链接]
    C --> D[循环处理<br/>每条新闻]
    D --> E[HTTP Request<br/>GET 新闻详情]
    E --> F[HTML Extract<br/>提取标题/正文/时间]
    F --> G[数据清洗<br/>去除HTML标签]
    G --> H[HTTP Request<br/>POST /api/news/ingest]
    H --> I[日志记录]
```

#### Workflow 2: 异常监控

```mermaid
graph LR
    A[定时触发<br/>每5分钟] --> B[HTTP Request<br/>GET /health]
    B --> C{状态正常?}
    C -->|否| D[发送告警邮件]
    C -->|是| E[记录健康日志]
```

---

### 3.4 AI 模块

#### 3.4.1 Ollama LLM

**作用**: 本地大语言模型推理

**推荐模型**:

- `qwen2.5:7b` - 中文优化，适合问答
- `llama3.1:8b` - 综合性能好
- `gemma2:9b` - 轻量级

**API 调用示例**:

```python
import requests

response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "qwen2.5:7b",
        "prompt": "基于以下新闻回答问题...",
        "stream": False
    }
)
```

#### 3.4.2 Embedding Model

**作用**: 文本向量化

**推荐模型**:

- `mxbai-embed-large` - 高质量通用向量（1024维）
- `nomic-embed-text` - 轻量级（768维）

**向量化流程**:

```python
from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="mxbai-embed-large")
vector = embeddings.embed_query("文本内容")
```

#### 3.4.3 FAISS Vector Store

**作用**: 高效向量检索

**索引类型**:

- `IndexFlatL2` - 精确检索（小数据量 < 10万）
- `IndexIVFFlat` - 倒排索引（大数据量 > 10万）

**检索流程**:

```python
import faiss
import numpy as np

# 加载索引
index = faiss.read_index("news_vectors.index")

# 检索 Top-K
query_vector = np.array([...]).astype('float32')
distances, indices = index.search(query_vector, k=5)
```

---

## 4. 数据流详解

### 4.1 新闻入库流程

```mermaid
sequenceDiagram
    participant N as n8n
    participant API as Flask API
    participant DB as SQLite
    participant EMB as Embedding Model
    participant FAISS as FAISS Index

    N->>API: POST /api/news/ingest<br/>{title, content, url, ...}
    API->>API: 数据验证
    API->>DB: 查询 URL 是否存在

    alt URL 已存在
        DB-->>API: 返回已存在
        API-->>N: 409 Conflict
    else URL 不存在
        API->>DB: INSERT 新闻记录
        DB-->>API: 返回 news_id
        API->>EMB: 生成向量<br/>embed_query(content)
        EMB-->>API: 返回 vector
        API->>FAISS: 添加向量<br/>index.add(vector)
        FAISS-->>API: 返回索引 ID
        API->>DB: 更新 indexed=True
        API-->>N: 200 OK<br/>{news_id, status}
    end
```

### 4.2 RAG 问答流程

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as Flask API
    participant EMB as Embedding Model
    participant FAISS as FAISS Index
    participant LLM as Ollama
    participant BD as 百度搜索
    participant DB as SQLite

    U->>FE: 输入问题
    FE->>API: POST /api/rag/query<br/>{question}
    API->>EMB: 向量化问题
    EMB-->>API: query_vector
    API->>FAISS: 检索 Top-5
    FAISS-->>API: [indices, scores]

    alt scores[0] >= 0.6 且 len >= 3
        API->>API: 检索质量合格
    else 检索质量不足
        API->>BD: 调用百度搜索
        BD-->>API: 补充结果
    end

    API->>DB: 获取新闻详情<br/>by indices
    DB-->>API: news_list
    API->>API: 构建 Prompt<br/>问题 + 上下文
    API->>LLM: POST /api/generate
    LLM-->>API: 生成答案
    API->>DB: 保存历史记录
    API-->>FE: 返回答案 + 来源
    FE-->>U: 展示结果
```

### 4.3 聚类分析流程

```mermaid
sequenceDiagram
    participant U as User
    participant API as Flask API
    participant DB as SQLite
    participant FAISS as FAISS Index
    participant SK as Scikit-learn
    participant LLM as Ollama

    U->>API: POST /api/cluster/analyze<br/>{start_date, end_date, n_clusters}
    API->>DB: 查询时间范围内的新闻
    DB-->>API: news_ids
    API->>FAISS: 提取对应向量
    FAISS-->>API: vectors
    API->>SK: PCA 降维<br/>1024 -> 50
    SK-->>API: reduced_vectors
    API->>SK: KMeans(n_clusters)
    SK-->>API: cluster_labels

    loop 每个聚类
        API->>DB: 获取聚类内新闻
        DB-->>API: cluster_news
        API->>API: TF-IDF 提取关键词
        API->>LLM: 生成主题标签<br/>（可选）
        LLM-->>API: topic_label
    end

    API->>SK: t-SNE 降维<br/>用于可视化
    SK-->>API: 2D coordinates
    API-->>U: 返回聚类结果 + 可视化数据
```

---

## 5. 鉴权流程

### 5.1 JWT 认证流程

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as Flask API
    participant DB as SQLite

    U->>FE: 输入邮箱/密码
    FE->>API: POST /api/auth/login<br/>{email, password}
    API->>DB: 查询用户
    DB-->>API: user_info
    API->>API: 验证密码<br/>bcrypt.check()

    alt 密码正确
        API->>API: 生成 JWT Token<br/>{user_id, exp: 24h}
        API-->>FE: 200 OK<br/>{token, user_info}
        FE->>FE: 存储 Token<br/>localStorage
        FE-->>U: 跳转到仪表盘
    else 密码错误
        API->>DB: 记录失败次数
        API-->>FE: 401 Unauthorized
        FE-->>U: 显示错误
    end
```

### 5.2 API 请求鉴权

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant MW as Auth Middleware
    participant API as API Handler

    FE->>MW: GET /api/news<br/>Header: Authorization: Bearer {token}
    MW->>MW: 解析 Token

    alt Token 有效
        MW->>MW: 提取 user_id
        MW->>API: 传递请求 + user_id
        API-->>MW: 返回数据
        MW-->>FE: 200 OK
    else Token 无效/过期
        MW-->>FE: 401 Unauthorized
    end
```

---

## 6. 扩展性设计

### 6.1 水平扩展

**前端**:

- 静态文件通过 CDN 分发
- Nginx 负载均衡

**后端**:

```mermaid
graph LR
    A[Nginx LB] --> B[Flask Instance 1]
    A --> C[Flask Instance 2]
    A --> D[Flask Instance N]

    B --> E[(SQLite)]
    C --> E
    D --> E

    B --> F[FAISS Shared]
    C --> F
    D --> F
```

**注意**: SQLite 不支持高并发写入，建议迁移到 PostgreSQL/MySQL

### 6.2 缓存策略

```mermaid
graph LR
    A[API Request] --> B{Redis Cache?}
    B -->|Hit| C[返回缓存]
    B -->|Miss| D[查询数据库]
    D --> E[写入缓存]
    E --> F[返回结果]
```

**缓存场景**:

- 热门问答结果（TTL: 1小时）
- 关键词统计（TTL: 30分钟）
- 新闻列表（TTL: 5分钟）

### 6.3 异步任务

使用 Celery 处理耗时操作:

- 批量新闻入库
- 聚类分析
- 报告生成

```python
# tasks.py
@celery.task
def batch_ingest_news(news_list):
    for news in news_list:
        # 入库逻辑
        pass
```

---

## 7. 监控与可观测性

### 7.1 健康检查

```python
@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": check_db(),
            "faiss": check_faiss(),
            "ollama": check_ollama()
        }
    }
```

### 7.2 日志架构

```mermaid
graph LR
    A[应用日志] --> B[文件日志]
    A --> C[控制台输出]
    B --> D[日志聚合<br/>可选: ELK]
```

**日志级别**:

- DEBUG: 详细调试信息
- INFO: 常规操作（入库、查询）
- WARNING: 警告（检索质量不足、回退搜索）
- ERROR: 错误（API 调用失败、数据库异常）

### 7.3 监控指标

**系统指标**:

- CPU/内存使用率
- 磁盘空间
- 网络流量

**应用指标**:

- API 请求量（QPS）
- 响应时间（P50/P95/P99）
- 错误率
- 数据库连接数

**业务指标**:

- 新闻入库量（条/小时）
- RAG 问答次数
- 回退搜索触发率
- 用户活跃度

---

## 8. 安全架构

### 8.1 网络安全

```mermaid
graph TB
    A[Internet] --> B[Firewall]
    B --> C[Nginx SSL Termination]
    C --> D[Flask App]
    D --> E[(Database)]

    F[Admin] --> G[VPN] --> D
```

### 8.2 数据安全

**传输加密**:

- HTTPS (TLS 1.3)
- WebSocket over SSL

**存储加密**:

- 密码: bcrypt (cost=12)
- 敏感配置: 环境变量
- 数据库: 可选加密（SQLCipher）

### 8.3 API 安全

**防护措施**:

- JWT 认证
- 速率限制（100 次/分钟/用户）
- CORS 白名单
- SQL 注入防护（参数化查询）
- XSS 防护（输入转义）

---

## 9. 部署架构

### 9.1 单机部署（推荐用于 MVP）

```mermaid
graph TB
    subgraph "单台服务器"
        A[Nginx :80/443]
        B[Frontend静态文件]
        C[Flask :5000]
        D[Ollama :11434]
        E[n8n :5678]
        F[(SQLite)]
        G[FAISS Index]
        H[Redis :6379]
    end

    A --> B
    A --> C
    C --> D
    C --> F
    C --> G
    C --> H
    E --> C
```

### 9.2 Docker Compose 部署

```yaml
version: "3.8"
services:
  nginx:
    image: nginx:alpine
    ports: [80:80, 443:443]

  frontend:
    build: ./frontend

  backend:
    build: ./backend
    ports: [5000:5000]
    depends_on: [redis, ollama]

  ollama:
    image: ollama/ollama
    ports: [11434:11434]
    volumes: [ollama_data:/root/.ollama]

  n8n:
    image: n8nio/n8n
    ports: [5678:5678]

  redis:
    image: redis:alpine
    ports: [6379:6379]
```

---

## 10. 技术选型理由

| 技术          | 理由                         |
| ------------- | ---------------------------- |
| **React**     | 生态成熟、组件化、性能好     |
| **Vite**      | 开发体验佳、构建速度快       |
| **Flask**     | 轻量级、易于集成 LangChain   |
| **LangChain** | RAG 开发框架、组件丰富       |
| **FAISS**     | 高效向量检索、支持大规模索引 |
| **SQLite**    | 零配置、适合中小规模数据     |
| **Ollama**    | 本地部署、隐私保护、成本低   |
| **n8n**       | 可视化工作流、易于维护       |
| **Docker**    | 环境一致性、部署便捷         |

---

## 11. 未来演进方向

### 11.1 短期优化（1-3 个月）

- 引入 PostgreSQL 替代 SQLite
- 增加 Redis 缓存层
- 前端国际化（i18n）
- 移动端适配

### 11.2 中期扩展（3-6 个月）

- 多模态支持（图片新闻）
- 实时新闻推送（WebSocket）
- 用户个性化推荐
- 分布式爬虫（Scrapy）

### 11.3 长期规划（6-12 个月）

- 微服务化改造
- Kubernetes 部署
- 多租户支持
- 数据湖集成

---

**文档状态**: ✅ 已评审  
**最后更新**: 2026-6-30
