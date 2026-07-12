# XU-News-AI-RAG API 规范文档

**版本**: v1.0 (OpenAPI 3.0)  
**创建日期**: 2026-6-30  
**Base URL**: `http://localhost:5000/api/v1`

---

## 1. API 概述

### 1.1 认证方式

所有 API（除注册/登录）需要在 Header 中携带 JWT Token:

```
Authorization: Bearer <token>
```

### 1.2 通用响应格式

**成功响应**:

```json
{
    "code": 0,
    "message": "success",
    "data": { ... }
}
```

**错误响应**:

```json
{
  "code": 40001,
  "message": "Invalid token",
  "data": null
}
```

### 1.3 错误码定义

| 错误码 | 说明                   |
| ------ | ---------------------- |
| 0      | 成功                   |
| 40000  | 参数错误               |
| 40001  | 未认证                 |
| 40003  | 权限不足               |
| 40004  | 资源不存在             |
| 40009  | 资源冲突（如重复注册） |
| 42901  | 请求过于频繁           |
| 50000  | 服务器内部错误         |
| 50003  | 外部服务不可用         |

### 1.4 分页参数

统一分页参数:

```
?page=1&page_size=20
```

分页响应:

```json
{
    "code": 0,
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    }
}
```

---

## 2. API 端点列表

### 2.1 认证模块 (Auth)

#### 2.1.1 用户注册

**接口**: `POST /auth/register`  
**认证**: 不需要

**请求体**:

```json
{
  "email": "user@example.com",
  "password": "Password123",
  "username": "User1"
}
```

**参数校验**:

- `email`: 必填，邮箱格式
- `password`: 必填，8-32 位，包含字母和数字
- `username`: 可选，2-50 个字符

**响应** (200 OK):

```json
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "user_id": 123,
    "email": "user@example.com",
    "username": "User1",
    "created_at": "2026-6-30T10:30:00Z"
  }
}
```

**错误响应** (409 Conflict):

```json
{
  "code": 40009,
  "message": "邮箱已被注册",
  "data": null
}
```

---

#### 2.1.2 用户登录

**接口**: `POST /auth/login`  
**认证**: 不需要

**请求体**:

```json
{
  "email": "user@example.com",
  "password": "Password123"
}
```

**响应** (200 OK):

```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400,
    "user": {
      "user_id": 123,
      "email": "user@example.com",
      "username": "User1",
      "role": "user"
    }
  }
}
```

**错误响应** (401 Unauthorized):

```json
{
  "code": 40001,
  "message": "邮箱或密码错误",
  "data": {
    "remaining_attempts": 3
  }
}
```

**账户锁定** (403 Forbidden):

```json
{
  "code": 40003,
  "message": "账户已锁定，请 15 分钟后重试",
  "data": {
    "locked_until": "2026-6-30T11:00:00Z"
  }
}
```

---

#### 2.1.3 Token 刷新

**接口**: `POST /auth/refresh`  
**认证**: 需要（使用即将过期的 Token）

**请求头**:

```
Authorization: Bearer <old_token>
```

**响应** (200 OK):

```json
{
  "code": 0,
  "message": "Token 刷新成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  }
}
```

---

#### 2.1.4 获取当前用户信息

**接口**: `GET /auth/me`  
**认证**: 需要

**响应** (200 OK):

```json
{
  "code": 0,
  "data": {
    "user_id": 123,
    "email": "user@example.com",
    "username": "User1",
    "avatar_url": "https://example.com/avatar.jpg",
    "role": "user",
    "created_at": "2025-10-01T08:00:00Z"
  }
}
```

---

#### 2.1.5 密码重置（预留）

**接口**: `POST /auth/reset-password`  
**认证**: 不需要

**流程**:

1. 用户请求重置，系统发送验证码到邮箱
2. 用户提交验证码 + 新密码

---

### 2.2 新闻管理模块 (News)

#### 2.2.1 新闻入库（n8n 回调）

**接口**: `POST /news/ingest`  
**认证**: API Key（n8n 专用）

**请求头**:

```
X-API-Key: <n8n_api_key>
```

**请求体**:

```json
{
  "title": "OpenAI 发布 GPT-5",
  "content": "OpenAI 今日宣布...",
  "url": "https://example.com/news/gpt5",
  "source": "科技日报",
  "author": "张三",
  "published_at": "2026-6-30T10:00:00Z",
  "category": "科技",
  "tags": ["AI", "OpenAI", "GPT"]
}
```

**参数校验**:

- `title`: 必填，1-500 字符
- `content`: 必填，至少 100 字符
- `url`: 必填，唯一
- `source`: 可选
- `published_at`: 可选，ISO 8601 格式

**响应** (200 OK):

```json
{
  "code": 0,
  "message": "入库成功",
  "data": {
    "news_id": 1001,
    "faiss_id": 1001,
    "vector_indexed": true,
    "duplicate": false
  }
}
```

**去重响应** (409 Conflict):

```json
{
  "code": 40009,
  "message": "新闻已存在",
  "data": {
    "news_id": 998,
    "url": "https://example.com/news/gpt5"
  }
}
```

---

#### 2.2.2 获取新闻列表

**接口**: `GET /news`  
**认证**: 需要

**查询参数**:

```
?page=1
&page_size=20
&category=科技
&start_date=2025-10-01
&end_date=2026-6-30
&keyword=AI
&sort_by=published_at  # published_at, view_count
&order=desc            # asc, desc
```

**响应** (200 OK):

```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "news_id": 1001,
        "title": "OpenAI 发布 GPT-5",
        "summary": "OpenAI 宣布最新模型...",
        "url": "https://example.com/news/gpt5",
        "source": "科技日报",
        "category": "科技",
        "tags": ["AI", "OpenAI"],
        "published_at": "2026-6-30T10:00:00Z",
        "view_count": 1523,
        "reference_count": 15
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

---

#### 2.2.3 获取新闻详情

**接口**: `GET /news/{news_id}`  
**认证**: 需要

**响应** (200 OK):

```json
{
  "code": 0,
  "data": {
    "news_id": 1001,
    "title": "OpenAI 发布 GPT-5",
    "content": "完整正文内容...",
    "summary": "摘要...",
    "url": "https://example.com/news/gpt5",
    "source": "科技日报",
    "author": "张三",
    "category": "科技",
    "tags": ["AI", "OpenAI", "GPT"],
    "published_at": "2026-6-30T10:00:00Z",
    "crawled_at": "2026-6-30T10:05:00Z",
    "view_count": 1523,
    "reference_count": 15
  }
}
```

**错误响应** (404 Not Found):

```json
{
  "code": 40004,
  "message": "新闻不存在",
  "data": null
}
```

---

#### 2.2.4 删除新闻（软删除）

**接口**: `DELETE /news/{news_id}`  
**认证**: 需要（仅管理员）

**响应** (200 OK):

```json
{
  "code": 0,
  "message": "删除成功",
  "data": null
}
```

---

### 2.3 RAG 检索问答模块 (RAG)

#### 2.3.1 RAG 问答

**接口**: `POST /rag/query`  
**认证**: 需要

**请求体**:

```json
{
    "question": "最近关于 AI 的新闻有哪些？",
    "top_k": 5,
    "enable_fallback": true,  # 是否启用回退搜索
    "llm_model": "qwen2.5:7b"
}
```

**参数说明**:

- `question`: 必填，用户问题
- `top_k`: 可选，检索新闻数量（默认 5）
- `enable_fallback`: 可选，是否启用百度搜索回退（默认 true）
- `llm_model`: 可选，指定 LLM 模型（默认使用系统配置）

**响应** (200 OK):

```json
{
    "code": 0,
    "data": {
        "question": "最近关于 AI 的新闻有哪些？",
        "answer": "根据检索到的新闻，最近关于 AI 的主要动态包括：\n1. OpenAI 发布 GPT-5...\n2. 百度发布文心一言 4.0...\n（来源：新闻 [1001][1005]）",
        "sources": [
            {
                "news_id": 1001,
                "title": "OpenAI 发布 GPT-5",
                "summary": "...",
                "url": "https://example.com/news/gpt5",
                "score": 0.92,
                "source_type": "local"  # local 或 web
            },
            {
                "news_id": 1005,
                "title": "百度发布文心一言 4.0",
                "summary": "...",
                "url": "https://example.com/news/wenxin",
                "score": 0.85,
                "source_type": "local"
            }
        ],
        "retrieval_stats": {
            "retrieval_method": "faiss",  # faiss, hybrid
            "total_retrieved": 5,
            "avg_score": 0.88,
            "fallback_triggered": false
        },
        "llm_stats": {
            "model": "qwen2.5:7b",
            "tokens_used": 1523,
            "response_time": 3.2
        }
    }
}
```

**回退搜索示例** (当本地检索质量不足时):

```json
{
  "data": {
    "answer": "...",
    "sources": [
      {
        "title": "本地新闻标题",
        "source_type": "local",
        "score": 0.55
      },
      {
        "title": "百度搜索结果标题",
        "source_type": "web",
        "url": "https://baidu.com/link/..."
      }
    ],
    "retrieval_stats": {
      "retrieval_method": "hybrid",
      "fallback_triggered": true,
      "fallback_reason": "低相似度 (avg_score < 0.6)"
    }
  }
}
```

---

#### 2.3.2 纯检索（不生成答案）

**接口**: `POST /rag/search`  
**认证**: 需要

**请求体**:

```json
{
  "query": "AI 发展",
  "top_k": 10
}
```

**响应** (200 OK):

```json
{
  "code": 0,
  "data": {
    "results": [
      {
        "news_id": 1001,
        "title": "OpenAI 发布 GPT-5",
        "summary": "...",
        "score": 0.92
      }
    ],
    "total": 10
  }
}
```

---

### 2.4 聚类分析模块 (Cluster)

#### 2.4.1 创建聚类任务

**接口**: `POST /cluster/analyze`  
**认证**: 需要

**请求体**:

```json
{
    "start_date": "2025-10-01",
    "end_date": "2026-6-30",
    "n_clusters": 5,
    "algorithm": "kmeans",  # kmeans, dbscan
    "category": "科技"       # 可选：仅分析特定分类
}
```

**响应** (202 Accepted - 异步任务):

```json
{
    "code": 0,
    "message": "聚类任务已创建",
    "data": {
        "task_id": "cluster_20251009_abc123",
        "status": "pending",
        "estimated_time": 30  # 秒
    }
}
```

---

#### 2.4.2 获取聚类结果

**接口**: `GET /cluster/result/{task_id}`  
**认证**: 需要

**响应** (200 OK):

```json
{
    "code": 0,
    "data": {
        "task_id": "cluster_20251009_abc123",
        "status": "completed",  # pending, running, completed, failed
        "result": {
            "total_news": 500,
            "n_clusters": 5,
            "silhouette_score": 0.68,
            "clusters": [
                {
                    "cluster_id": 0,
                    "topic": "AI 技术发展",
                    "keywords": ["AI", "GPT", "模型"],
                    "news_count": 120,
                    "news_ids": [1001, 1005, 1010],
                    "sample_titles": [
                        "OpenAI 发布 GPT-5",
                        "百度发布文心一言 4.0"
                    ]
                },
                {
                    "cluster_id": 1,
                    "topic": "科技股市场",
                    "keywords": ["股价", "科技股", "投资"],
                    "news_count": 85,
                    "news_ids": [1002, 1008],
                    "sample_titles": [...]
                }
            ],
            "visualization": {
                "coordinates": [
                    {"x": 0.5, "y": 0.3, "cluster_id": 0, "news_id": 1001},
                    {"x": 0.2, "y": 0.8, "cluster_id": 1, "news_id": 1002}
                ]
            }
        },
        "created_at": "2026-6-30T10:30:00Z"
    }
}
```

**任务进行中** (202 Accepted):

```json
{
    "code": 0,
    "data": {
        "task_id": "cluster_20251009_abc123",
        "status": "running",
        "progress": 60  # 百分比
    }
}
```

---

#### 2.4.3 导出聚类报告

**接口**: `GET /cluster/report/{task_id}`  
**认证**: 需要

**查询参数**:

```
?format=pdf  # pdf, markdown, json
```

**响应** (200 OK):

```
Content-Type: application/pdf
Content-Disposition: attachment; filename="cluster_report_20251009.pdf"

<PDF 二进制数据>
```

---

### 2.5 关键词统计模块 (Keyword)

#### 2.5.1 获取关键词 Top10

**接口**: `GET /keyword/top`  
**认证**: 需要

**查询参数**:

```
?time_range=daily      # daily, weekly, monthly
&start_date=2026-6-30
&end_date=2026-6-30
&category=科技         # 可选
```

**响应** (200 OK):

```json
{
    "code": 0,
    "data": {
        "time_range": "daily",
        "start_date": "2026-6-30",
        "end_date": "2026-6-30",
        "keywords": [
            {
                "word": "AI",
                "count": 156,
                "trend": "up"  # up, down, stable
            },
            {
                "word": "GPT",
                "count": 89,
                "trend": "up"
            },
            {
                "word": "OpenAI",
                "count": 67,
                "trend": "stable"
            }
        ],
        "total_news": 500
    }
}
```

---

#### 2.5.2 关键词趋势分析

**接口**: `GET /keyword/trend/{keyword}`  
**认证**: 需要

**查询参数**:

```
?days=30  # 最近 30 天
```

**响应** (200 OK):

```json
{
  "code": 0,
  "data": {
    "keyword": "AI",
    "trend_data": [
      {
        "date": "2025-10-01",
        "count": 45
      },
      {
        "date": "2025-10-02",
        "count": 52
      }
    ]
  }
}
```

---

### 2.6 历史记录模块 (History)

#### 2.6.1 获取问答历史

**接口**: `GET /history/queries`  
**认证**: 需要

**查询参数**:

```
?page=1
&page_size=20
&start_date=2025-10-01
&end_date=2026-6-30
```

**响应** (200 OK):

```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 5001,
        "question": "最近关于 AI 的新闻有哪些？",
        "answer": "根据检索...",
        "retrieval_method": "faiss",
        "llm_model": "qwen2.5:7b",
        "user_feedback": "positive",
        "created_at": "2026-6-30T10:30:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 20
  }
}
```

---

#### 2.6.2 删除历史记录

**接口**: `DELETE /history/queries/{query_id}`  
**认证**: 需要

**响应** (200 OK):

```json
{
  "code": 0,
  "message": "删除成功",
  "data": null
}
```

---

#### 2.6.3 提交反馈

**接口**: `POST /history/queries/{query_id}/feedback`  
**认证**: 需要

**请求体**:

```json
{
    "feedback": "positive",  # positive, negative
    "comment": "回答很准确"    # 可选
}
```

**响应** (200 OK):

```json
{
  "code": 0,
  "message": "反馈已提交",
  "data": null
}
```

---

### 2.7 系统管理模块 (System)

#### 2.7.1 健康检查

**接口**: `GET /system/health`  
**认证**: 不需要

**响应** (200 OK):

```json
{
  "status": "healthy",
  "timestamp": "2026-6-30T10:30:00Z",
  "services": {
    "database": {
      "status": "up",
      "response_time_ms": 5
    },
    "faiss": {
      "status": "up",
      "total_vectors": 15000
    },
    "ollama": {
      "status": "up",
      "models": ["qwen2.5:7b", "mxbai-embed-large"]
    },
    "redis": {
      "status": "up"
    }
  }
}
```

**服务异常** (503 Service Unavailable):

```json
{
  "status": "unhealthy",
  "services": {
    "ollama": {
      "status": "down",
      "error": "Connection refused"
    }
  }
}
```

---

#### 2.7.2 系统统计

**接口**: `GET /system/stats`  
**认证**: 需要（仅管理员）

**响应** (200 OK):

```json
{
  "code": 0,
  "data": {
    "total_news": 15000,
    "total_users": 256,
    "total_queries": 8952,
    "avg_response_time": 3.5,
    "cache_hit_rate": 0.62,
    "storage": {
      "db_size_mb": 256,
      "faiss_size_mb": 512
    }
  }
}
```

---

## 3. OpenAPI 3.0 规范（YAML）

```yaml
openapi: 3.0.3
info:
  title: XU-News-AI-RAG API
  version: 1.0.0
  description: 新闻智能检索与问答系统 API
  contact:
    email: api@xu-news.com

servers:
  - url: http://localhost:5000/api/v1
    description: 本地开发环境
  - url: https://api.xu-news.com/v1
    description: 生产环境

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    Error:
      type: object
      properties:
        code:
          type: integer
        message:
          type: string
        data:
          type: object
          nullable: true

    User:
      type: object
      properties:
        user_id:
          type: integer
        email:
          type: string
        username:
          type: string
        role:
          type: string
          enum: [user, admin]

    News:
      type: object
      properties:
        news_id:
          type: integer
        title:
          type: string
        content:
          type: string
        url:
          type: string
        source:
          type: string
        published_at:
          type: string
          format: date-time

paths:
  /auth/register:
    post:
      summary: 用户注册
      tags:
        - Auth
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - email
                - password
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  minLength: 8
                username:
                  type: string
      responses:
        "200":
          description: 注册成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    $ref: "#/components/schemas/User"
        "409":
          description: 邮箱已存在

  /auth/login:
    post:
      summary: 用户登录
      tags:
        - Auth
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                password:
                  type: string
      responses:
        "200":
          description: 登录成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    type: object
                    properties:
                      token:
                        type: string
                      user:
                        $ref: "#/components/schemas/User"

  /rag/query:
    post:
      summary: RAG 问答
      tags:
        - RAG
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - question
              properties:
                question:
                  type: string
                top_k:
                  type: integer
                  default: 5
                enable_fallback:
                  type: boolean
                  default: true
      responses:
        "200":
          description: 问答成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    type: object
                    properties:
                      question:
                        type: string
                      answer:
                        type: string
                      sources:
                        type: array
                        items:
                          $ref: "#/components/schemas/News"

  /news:
    get:
      summary: 获取新闻列表
      tags:
        - News
      security:
        - BearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: page_size
          in: query
          schema:
            type: integer
            default: 20
      responses:
        "200":
          description: 成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    type: object
                    properties:
                      items:
                        type: array
                        items:
                          $ref: "#/components/schemas/News"
                      total:
                        type: integer
```

---

## 4. 速率限制

| 用户类型    | 限制           |
| ----------- | -------------- |
| 普通用户    | 100 请求/分钟  |
| 管理员      | 1000 请求/分钟 |
| n8n API Key | 500 请求/分钟  |

**超限响应** (429 Too Many Requests):

```json
{
  "code": 42901,
  "message": "请求过于频繁，请稍后重试",
  "data": {
    "retry_after": 60
  }
}
```

---

## 5. Webhooks（预留）

### 5.1 新闻入库通知

当新闻成功入库时，向配置的 Webhook URL 发送通知:

**POST** `<your_webhook_url>`

```json
{
  "event": "news.ingested",
  "timestamp": "2026-6-30T10:30:00Z",
  "data": {
    "news_id": 1001,
    "title": "OpenAI 发布 GPT-5",
    "url": "https://example.com/news/gpt5"
  }
}
```

---

**文档状态**: ✅ 已评审  
**最后更新**: 2026-6-30
