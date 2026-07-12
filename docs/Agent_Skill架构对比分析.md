# Agent Skill 框架架构对比分析

**版本**: v1.0  
**创建日期**: 2026-07-12  
**依据**: [系统架构文档](file:///d:/homework/8/homework8/xu-ai-news-rag/docs/系统架构文档.md)、[Agent_Skill迁移文档](file:///d:/homework/8/homework8/xu-ai-news-rag/docs/Agent_Skill迁移文档.md)

---

## 1. 概述

本文档详细分析 XU-News-AI-RAG 项目在新增 Agent Skills 框架前后的架构差异，从架构层次、代码组织、设计模式、API 接口、工作流集成等多个维度进行对比。

---

## 2. 架构层次变化

### 2.1 改造前（传统 Flask 应用）

```
用户层 → 前端层 → API层 → 服务层(core/) → AI层 → 数据层
```

**特点**：
- 典型的三层架构（Controller-Service-DAO）
- AI 能力分散在 `core/` 目录
- 无 Agent 抽象层，功能直接通过 API 暴露

### 2.2 改造后（Agent Skill 框架）

```
用户层 → 前端层 → API层 → Agent层 → Skill/Tool层 → 服务层(core/) → AI层 → 数据层
```

**核心变化**：
- 新增 **Agent 层**：提供智能代理抽象，封装 RAG、分析、入库等能力
- 新增 **Skill/Tool 层**：将 AI 能力和外部工具封装为可复用模块

---

## 3. 代码组织结构变化

### 3.1 改造前的目录结构

```
backend/
├── apis/              # API 路由
├── core/              # 核心模块（Embedding、LLM、RAG、FAISS）
├── services/          # 业务逻辑（搜索回退、爬虫）
├── db/                # 数据库
├── auth/              # 认证
└── app.py
```

### 3.2 改造后的目录结构

```
backend/
├── apis/
│   └── agent_api.py   # Agent 统一接口（新增）
├── agent/             # Agent Skill 框架层（新增）
│   ├── base_agent.py  # Agent 基类
│   ├── news_agent.py  # NewsAgent 实现类
│   ├── memory.py      # 记忆管理
│   ├── planner.py     # 规划器
│   ├── skills/        # Skill 模块（4个）
│   │   ├── retrieval_skill.py
│   │   ├── generation_skill.py
│   │   ├── analysis_skill.py
│   │   └── ingestion_skill.py
│   └── tools/         # Tool 工具（4个）
│       ├── search_tool.py
│       ├── crawler_tool.py
│       ├── database_tool.py
│       └── email_tool.py
├── core/              # 保留，作为底层实现
├── services/          # 降级为工具实现
├── db/
├── auth/
└── app.py
```

---

## 4. 核心设计模式变化

| 维度 | 改造前 | 改造后 |
|------|--------|--------|
| **架构模式** | 传统三层架构（Controller-Service-DAO） | Agent 架构（Agent-Skill-Tool-Memory-Planner） |
| **能力封装** | AI 能力分散在 `core/` 目录，无统一封装 | 封装为可复用的 Skill 和 Tool |
| **工具调用** | 外部工具直接在服务层调用 | 通过 Tool 层统一调用，支持动态选择 |
| **记忆管理** | 查询历史仅存储在数据库 | NewsMemory 模块管理对话历史和用户画像 |
| **任务规划** | 无规划能力，线性执行 | NewsPlanner 实现任务类型分类和步骤规划 |

---

## 5. 核心类设计对比

### 5.1 改造前：无 Agent 抽象

```python
# 直接在 API 层调用核心模块
@app.route('/api/search/ask', methods=['POST'])
def ask():
    question = request.json.get('question')
    from core.rag import RAGPipeline
    rag = RAGPipeline()
    result = rag.query(question)
    return jsonify(result)
```

### 5.2 改造后：Agent Skill 框架

```python
class NewsAgent(BaseAgent):
    def __init__(self):
        # 注册 Skill 和 Tool
        self.register_skill('retrieval', RetrievalSkill())
        self.register_skill('generation', GenerationSkill())
        self.register_skill('analysis', AnalysisSkill())
        self.register_skill('ingestion', IngestionSkill())
        self.register_tool('search', SearchTool())
        self.register_tool('crawler', CrawlerTool())
        self.memory = NewsMemory()
        self.planner = NewsPlanner()
    
    async def answer_question(self, question, user_id):
        # 规划 → 调用 Skill/Tool → 更新记忆
        plan = self.planner.plan(question, self)
        result = await self.execute(question, context)
        self.memory.add_message(user_id, 'user', question)
        return result
```

---

## 6. API 接口变化

### 6.1 改造前的 API 设计（分散式）

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/search/ask` | POST | RAG 问答 |
| `/api/ingest` | POST | 新闻入库 |
| `/api/reports/clusters` | GET | 聚类分析 |
| `/api/reports/keywords` | GET | 关键词统计 |

### 6.2 改造后的 API 设计（统一 Agent 接口）

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/agent/query` | POST | Agent 智能问答（统一入口） |
| `/api/agent/analyze` | POST | Agent 分析（聚类/关键词/趋势） |
| `/api/agent/ingest` | POST | Agent 批量入库 |
| `/api/agent/memory` | GET/DELETE | Agent 记忆管理 |
| `/api/agent/skills` | GET | 获取已注册 Skill 列表 |
| `/api/agent/tools` | GET | 获取已注册 Tool 列表 |

---

## 7. n8n 工作流集成变化

### 7.1 改造前：n8n 直接调用后端 API

```
n8n → HTTP节点 → /api/ingest（直接入库）
n8n → HTTP节点 → /api/search/ask（直接问答）
```

**问题**：n8n 与后端 API 紧密耦合，无法利用 Agent 的智能规划能力。

### 7.2 改造后：n8n 通过 Agent API 调用

```
n8n → Agent Query 节点 → /api/agent/query（智能问答）
n8n → Agent Analyze 节点 → /api/agent/analyze（分析任务）
n8n → Agent Ingest 节点 → /api/agent/ingest（批量入库）
n8n → Tool Search 节点 → 回退搜索
n8n → Memory Read/Write 节点 → 记忆管理
```

**优势**：通过统一 Agent API 实现低代码编排，支持智能任务规划。

---

## 8. 数据流向变化

### 8.1 改造前的 RAG 流程（线性）

```
用户 → API → RAGPipeline → Embedding → FAISS → LLM → 返回结果
```

**特点**：线性执行，无记忆，无规划。

### 8.2 改造后的 RAG 流程（Agent 驱动）

```
用户 → API → NewsAgent → NewsPlanner（规划）
    → RetrievalSkill（检索）→ FAISS/重排序
    → SearchTool（回退搜索，如需要）
    → GenerationSkill（生成）→ LLM
    → NewsMemory（更新记忆）
    → 返回结果（答案+来源+执行计划）
```

**特点**：
1. 规划器根据任务类型制定执行计划
2. 支持回退搜索（本地检索不足时自动触发）
3. 自动更新对话记忆，支持上下文对话

---

## 9. 扩展性设计变化

### 9.1 改造前：硬编码扩展

```python
# 新增功能需要修改多个文件
# 1. 在 core/ 目录新增模块
# 2. 在 services/ 目录新增服务
# 3. 在 apis/ 目录新增路由
# 4. 修改 app.py 注册蓝图
```

**问题**：修改成本高，耦合度高，难以维护。

### 9.2 改造后：插件式扩展

```python
# 新增 Skill 只需继承基类并注册
class CustomSkill(BaseSkill):
    def execute(self, **kwargs):
        pass

# 注册到 Agent
agent = NewsAgent()
agent.register_skill('custom', CustomSkill())

# 新增 Tool 同理
class CustomTool(BaseTool):
    def execute(self, **kwargs):
        pass

agent.register_tool('custom', CustomTool())
```

**优势**：插件式注册，新增能力只需注册，无需修改现有代码。

---

## 10. Skill 与 Tool 模块详解

### 10.1 Skill 模块

| Skill 名称 | 职责 | 核心方法 |
|-----------|------|---------|
| **RetrievalSkill** | 语义检索与重排序 | `search()`, `rerank()`, `hybrid_search()` |
| **GenerationSkill** | LLM 生成与摘要 | `generate()`, `summarize()`, `extract_keywords()` |
| **AnalysisSkill** | 聚类分析与统计 | `cluster_analysis()`, `keyword_statistics()`, `trend_analysis()` |
| **IngestionSkill** | 数据入库与去重 | `ingest_structured()`, `ingest_unstructured()`, `batch_ingest()` |

### 10.2 Tool 模块

| Tool 名称 | 职责 | 核心方法 |
|-----------|------|---------|
| **SearchTool** | 外部搜索 | `search_baidu()`, `search_rss()`, `search_local()` |
| **CrawlerTool** | 网页抓取 | `crawl_page()`, `check_robots()`, `extract_content()` |
| **DatabaseTool** | 数据库操作 | `query()`, `insert()`, `update()`, `delete()` |
| **EmailTool** | 邮件发送 | `send_email()`, `send_notification()`, `send_report()` |

---

## 11. 架构优势对比

| 优势 | 改造前 | 改造后 |
|------|--------|--------|
| **统一开发规范** | ❌ 无统一规范 | ✅ Agent Skill 框架提供标准化开发模式 |
| **能力复用** | ❌ AI 能力分散，难以复用 | ✅ Skill/Tool 封装为独立模块 |
| **工具选择** | ❌ 硬编码调用 | ✅ Planner 动态选择工具 |
| **上下文对话** | ❌ 无记忆管理 | ✅ Memory 模块支持上下文记忆 |
| **低代码编排** | ❌ n8n 与后端耦合 | ✅ 统一 Agent API 支持低代码编排 |
| **可扩展性** | ❌ 修改成本高 | ✅ 插件式注册，新增能力只需注册 |
| **可维护性** | ❌ 代码耦合度高 | ✅ 模块化设计，降低耦合 |

---

## 12. 总结

### 12.1 核心变化

新增 Agent Skills 框架后，项目从**传统的三层架构**演进为**完整的智能代理架构**：

1. **新增 Agent 层**：提供统一的智能代理抽象，封装 RAG、分析、入库等能力
2. **Skill/Tool 模块化**：将 AI 能力和外部工具封装为可复用、可扩展的模块
3. **记忆与规划**：新增 Memory 和 Planner 模块，支持上下文对话和任务规划
4. **统一 API 入口**：通过 `/api/agent/*` 接口提供统一的智能服务
5. **n8n 深度集成**：通过标准化接口支持低代码工作流编排

### 12.2 改造收益

| 收益 | 描述 |
|------|------|
| **智能代理能力封装** | 将 AI 能力封装为可复用的 Skill 和 Tool |
| **统一开发规范** | Agent Skill 框架提供标准化的开发模式 |
| **可扩展性** | 新增能力只需注册新的 Skill/Tool |
| **可维护性** | 模块化设计降低代码耦合度 |
| **低代码编排** | 通过统一 Agent API 实现 n8n 深度集成 |

---

**文档状态**: ✅ 已生成  
**最后更新**: 2026-07-12
