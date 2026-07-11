# XU-News-AI-RAG 功能差异分析报告

**版本**: v1.0  
**创建日期**: 2026-07-11  
**分析对象**: 当前代码实现 vs [PRD_ASSESSMENT.md](file:///d:/homework/8/homework8/xu-ai-news-rag/docs/PRD_ASSESSMENT.md)

---

## 1. 功能实现状态总览

| 功能模块   | PRD要求 | 当前状态  | 差距描述                            |
| ---------- | ------- | --------- | ----------------------------------- |
| 用户认证   | ✅      | ✅ 部分   | 缺少密码重置功能                    |
| 新闻采集   | ✅      | ⚠️ 部分   | n8n工作流存在但未完全集成           |
| 新闻入库   | ✅      | ✅        | 已实现结构化/非结构化入库           |
| 邮件通知   | ✅      | ❌ 未实现 | 仅前端有配置，无后端/工作流实现     |
| 内容管理   | ✅      | ❌ 未实现 | 缺少新闻列表管理、编辑、删除功能    |
| 智能问答   | ✅      | ✅        | RAG问答完整实现                     |
| 回退搜索   | ✅      | ⚠️ 部分   | 仅模拟实现，未接入真实百度API       |
| 聚类分析   | ✅      | ⚠️ 部分   | 使用随机向量，未从FAISS获取真实向量 |
| 关键词统计 | ✅      | ✅        | 已实现TF-IDF关键词Top10             |
| 历史记录   | ✅      | ❌ 未实现 | 后端有表结构，无API和前端页面       |

---

## 2. 详细差异分析

### 2.1 用户认证模块

**PRD要求**: 注册、登录、Token刷新、账户锁定、密码重置

**当前实现**:

- ✅ 用户注册（邮箱+密码，密码强度验证）
- ✅ 用户登录（JWT Token，24小时有效期）
- ✅ 账户锁定（失败5次锁定15分钟）
- ❌ **Token刷新** - 后端缺少 `/auth/refresh` 接口
- ❌ **密码重置** - 缺少邮箱验证码发送和密码重置功能

**代码位置**:

- [auth/jwt.py](file:///d:/homework/8/homework8/xu-ai-news-rag/backend/auth/jwt.py) - 仅实现 register/login/me

**差距**: 需要添加 `/auth/refresh` 和 `/auth/reset-password` 接口

---

### 2.2 新闻采集模块

**PRD要求**: RSS订阅、网页抓取、定时任务（n8n）、数据清洗、遵循robots.txt

**当前实现**:

- ✅ n8n工作流文件存在 (`news_crawler_workflow.json`)
- ✅ 后端支持非结构化数据入库（HTML解析）
- ❌ **n8n工作流未集成到后端** - 工作流文件仅为模板，未实际配置运行
- ❌ **robots.txt检查** - 爬虫工作流中未实现robots.txt检查
- ❌ **定时任务配置** - n8n需手动配置定时触发

**代码位置**:

- [workflows/news_crawler_workflow.json](file:///d:/homework/8/homework8/xu-ai-news-rag/workflows/news_crawler_workflow.json)
- [services/crawlers.py](file:///d:/homework/8/homework8/xu-ai-news-rag/backend/services/crawlers.py) - 存在但内容为空

**差距**: 需要配置n8n工作流并启动运行，添加robots.txt检查逻辑

---

### 2.3 新闻入库模块

**PRD要求**: 批量入库、去重检测、向量化、索引更新、Excel导入

**当前实现**:

- ✅ 结构化数据入库（JSON）
- ✅ 非结构化数据入库（纯文本/HTML）
- ✅ 去重检测（URL哈希）
- ✅ 文本切分（chunking）
- ✅ 向量化（Embedding）
- ✅ FAISS索引更新
- ⚠️ **Excel导入** - 后端支持Excel上传，但前端未实现文件上传界面

**代码位置**:

- [apis/ingest.py](file:///d:/homework/8/homework8/xu-ai-news-rag/backend/apis/ingest.py) - 支持Excel上传
- [frontend/src/pages/Ingest.jsx](file:///d:/homework/8/homework8/xu-ai-news-rag/frontend/src/pages/Ingest.jsx) - 仅支持JSON输入

**差距**: 前端Ingest页面需要添加Excel文件上传功能

---

### 2.4 邮件通知模块

**PRD要求**: 入库成功邮件通知、异常告警、自定义邮件模板

**当前实现**:

- ❌ **后端邮件服务** - 无邮件发送功能实现
- ❌ **n8n邮件节点** - `news_ingest_notify.json` 工作流存在但未配置
- ✅ 前端设置页面有SMTP配置项，但仅为本地状态，未传递到后端

**代码位置**:

- [workflows/news_ingest_notify.json](file:///d:/homework/8/homework8/xu-ai-news-rag/workflows/news_ingest_notify.json)
- [frontend/src/pages/Settings.jsx](file:///d:/homework/8/homework8/xu-ai-news-rag/frontend/src/pages/Settings.jsx) - SMTP配置仅前端展示

**差距**: 需要实现后端邮件服务，配置n8n邮件工作流

---

### 2.5 内容管理模块

**PRD要求**: 新闻列表查询、筛选、单条编辑、批量删除、数据上传

**当前实现**:

- ❌ **新闻列表API** - 缺少 `/api/news` GET 接口
- ❌ **新闻详情API** - 缺少 `/api/news/{id}` GET 接口
- ❌ **新闻删除API** - 缺少 `/api/news/{id}` DELETE 接口
- ❌ **新闻编辑API** - 缺少 `/api/news/{id}` PUT/PATCH 接口
- ❌ **前端管理页面** - 缺少新闻管理页面

**代码位置**:

- [db/dao.py](file:///d:/homework/8/homework8/xu-ai-news-rag/backend/db/dao.py) - ArticleDAO已有基础方法
- [frontend/src/services/api.js](file:///d:/homework/8/homework8/xu-ai-news-rag/frontend/src/services/api.js) - newsAPI有getNewsList/getNewsDetail但后端未实现

**差距**: 需要实现完整的新闻CRUD API和前端管理页面

---

### 2.6 智能问答模块

**PRD要求**: 语义检索、LLM推理、来源引用、历史记录

**当前实现**:

- ✅ 语义检索（FAISS）
- ✅ 重排序（Cross-Encoder）
- ✅ LLM推理（Ollama）
- ✅ 来源引用（显示相似度、重排分数）
- ✅ 查询日志记录（后端自动保存）

**代码位置**:

- [apis/search.py](file:///d:/homework/8/homework8/xu-ai-news-rag/backend/apis/search.py)
- [core/rag.py](file:///d:/homework/8/homework8/xu-ai-news-rag/backend/core/rag.py)
- [frontend/src/pages/Query.jsx](file:///d:/homework/8/homework8/xu-ai-news-rag/frontend/src/pages/Query.jsx)

**差距**: 无重大差距，功能完整

---

### 2.7 回退搜索模块

**PRD要求**: 质量检测、百度搜索API、结果合并、来源标注

**当前实现**:

- ✅ 质量检测（结果数和相似度阈值判断）
- ⚠️ **百度搜索API** - 仅模拟实现（mock_results），未接入真实百度API
- ✅ 结果合并（本地+网络来源）
- ✅ 来源标注（fallback标记）

**代码位置**:

- [services/search_fallback.py](file:///d:/homework/8/homework8/xu-ai-news-rag/backend/services/search_fallback.py) - `search_fallback` 返回模拟数据

**差距**: 需要配置百度API Key并实现真实搜索调用

---

### 2.8 聚类分析模块

**PRD要求**: K-Means/DBSCAN聚类、关键词提取、可视化（t-SNE）、报告导出

**当前实现**:

- ✅ K-Means聚类算法
- ✅ DBSCAN聚类算法
- ✅ 关键词提取（TF-IDF+jieba分词）
- ✅ t-SNE降维可视化
- ❌ **真实向量使用** - 使用随机向量而非FAISS中的真实向量
- ❌ **报告导出** - 缺少PDF/Markdown导出功能

**代码位置**:

- [apis/reports.py](file:///d:/homework/8/homework8/xu-ai-news-rag/backend/apis/reports.py) - 第156行使用 `np.random.rand()` 生成随机向量
- [frontend/src/pages/Reports.jsx](file:///d:/homework8/xu-ai-news-rag/frontend/src/pages/Reports.jsx) - 无导出按钮

**差距**: 需要实现从FAISS获取真实向量，添加报告导出功能

---

### 2.9 关键词统计模块

**PRD要求**: 时间维度筛选、关键词提取、频次统计、趋势分析、数据导出

**当前实现**:

- ✅ 时间维度筛选（daily/weekly/monthly）
- ✅ 关键词提取（TF-IDF）
- ✅ 频次统计与排序
- ❌ **趋势分析** - 缺少关键词趋势接口 `/api/report/topkeywords/trend`
- ❌ **数据导出** - 缺少CSV/JSON导出功能

**代码位置**:

- [apis/reports.py](file:///d:/homework/8/homework8/xu-ai-news-rag/backend/apis/reports.py) - 无趋势分析接口

**差距**: 需要添加趋势分析API和数据导出功能

---

### 2.10 历史记录模块

**PRD要求**: 问答历史查询、分页、删除、用户反馈

**当前实现**:

- ✅ 后端自动保存查询日志（QueryLog）
- ❌ **历史记录API** - 缺少 `/api/history/queries` GET/DELETE接口
- ❌ **用户反馈API** - 缺少 `/api/history/queries/{id}/feedback` 接口
- ❌ **前端历史记录页面** - 缺少历史记录展示页面

**代码位置**:

- [db/models.py](file:///d:/homework/8/homework8/xu-ai-news-rag/backend/db/models.py) - QueryLog表已定义
- [db/dao.py](file:///d:/homework/8/homework8/xu-ai-news-rag/backend/db/dao.py) - QueryLogDAO已定义基础方法

**差距**: 需要实现历史记录API和前端页面

---

## 3. n8n工作流专项差距

### 3.1 工作流文件分析

| 工作流文件                     | PRD要求    | 当前状态 | 差距           |
| ------------------------------ | ---------- | -------- | -------------- |
| `news_crawler_workflow.json`   | 新闻采集   | ✅ 存在  | 未配置运行     |
| `news_ingest_notify.json`      | 入库通知   | ✅ 存在  | 未配置邮件服务 |
| `news_ingest_notify_free.json` | 免费版通知 | ✅ 存在  | 未配置运行     |

### 3.2 n8n集成差距

| 要求             | 当前状态 | 差距                        |
| ---------------- | -------- | --------------------------- |
| 定时触发节点配置 | ❌       | 需要配置Cron定时任务        |
| HTTP请求节点配置 | ❌       | 需要配置新闻源URL           |
| HTML解析节点配置 | ❌       | 需要配置选择器              |
| 邮件发送节点配置 | ❌       | 需要配置SMTP服务器          |
| 异常处理配置     | ❌       | 需要配置重试和告警          |
| 工作流部署       | ❌       | 需要启动n8n服务并导入工作流 |

---

## 4. 前端页面差距

### 4.1 已实现页面

| 页面     | 文件                                                                                             | 状态             |
| -------- | ------------------------------------------------------------------------------------------------ | ---------------- |
| 登录     | [Login.jsx](file:///d:/homework/8/homework8/xu-ai-news-rag/frontend/src/pages/Login.jsx)         | ✅               |
| 注册     | [Register.jsx](file:///d:/homework/8/homework8/xu-ai-news-rag/frontend/src/pages/Register.jsx)   | ✅               |
| 仪表盘   | [Dashboard.jsx](file:///d:/homework/8/homework8/xu-ai-news-rag/frontend/src/pages/Dashboard.jsx) | ✅               |
| 数据入库 | [Ingest.jsx](file:///d:/homework/8/homework8/xu-ai-news-rag/frontend/src/pages/Ingest.jsx)       | ⚠️ 缺少Excel上传 |
| 智能问答 | [Query.jsx](file:///d:/homework/8/homework8/xu-ai-news-rag/frontend/src/pages/Query.jsx)         | ✅               |
| 分析报告 | [Reports.jsx](file:///d:/homework/8/homework8/xu-ai-news-rag/frontend/src/pages/Reports.jsx)     | ⚠️ 缺少导出功能  |
| 设置     | [Settings.jsx](file:///d:/homework8/xu-ai-news-rag/frontend/src/pages/Settings.jsx)              | ✅               |

### 4.2 缺少页面

| 页面     | PRD要求 | 描述                 |
| -------- | ------- | -------------------- |
| 新闻管理 | ✅      | 新闻列表、编辑、删除 |
| 历史记录 | ✅      | 用户问答历史、反馈   |
| 个人中心 | ✅      | 用户信息、修改密码   |

---

## 5. API接口差距

### 5.1 已实现接口

| 模块 | 接口                          | 状态 |
| ---- | ----------------------------- | ---- |
| 认证 | POST /api/auth/register       | ✅   |
|      | POST /api/auth/login          | ✅   |
|      | GET /api/auth/me              | ✅   |
| 入库 | POST /api/ingest/structured   | ✅   |
|      | POST /api/ingest/unstructured | ✅   |
| 搜索 | POST /api/ask                 | ✅   |
| 报告 | GET /api/report/clusters      | ✅   |
|      | GET /api/report/topkeywords   | ✅   |
| 健康 | GET /api/health               | ✅   |

### 5.2 缺少接口

| 模块     | 接口                                    | PRD要求 | 描述      |
| -------- | --------------------------------------- | ------- | --------- |
| 认证     | POST /api/auth/refresh                  | ✅      | Token刷新 |
|          | POST /api/auth/reset-password           | ✅      | 密码重置  |
| 新闻管理 | GET /api/news                           | ✅      | 新闻列表  |
|          | GET /api/news/{id}                      | ✅      | 新闻详情  |
|          | PUT /api/news/{id}                      | ✅      | 新闻编辑  |
|          | DELETE /api/news/{id}                   | ✅      | 新闻删除  |
| 历史记录 | GET /api/history/queries                | ✅      | 查询历史  |
|          | DELETE /api/history/queries/{id}        | ✅      | 删除历史  |
|          | POST /api/history/queries/{id}/feedback | ✅      | 用户反馈  |
| 关键词   | GET /api/report/topkeywords/trend       | ✅      | 趋势分析  |
| 聚类     | GET /api/report/clusters/export         | ✅      | 报告导出  |

---

## 6. 数据库差距

### 6.1 已实现表

| 表名        | 状态 | 描述         |
| ----------- | ---- | ------------ |
| users       | ✅   | 用户表       |
| articles    | ✅   | 文章表       |
| chunks      | ✅   | 文章切分块表 |
| query_logs  | ✅   | 查询日志表   |
| system_meta | ✅   | 系统元数据表 |

### 6.2 表结构完整性

| 表         | 差距 | 描述                                                   |
| ---------- | ---- | ------------------------------------------------------ |
| articles   | ⚠️   | 缺少标签字段的实际使用（tags字段已定义但未在前端展示） |
| query_logs | ✅   | 完整，包含用户反馈字段                                 |

---

## 7. 功能优先级建议

### P0 - 核心功能缺失

| 功能             | 影响                     | 建议完成时间 |
| ---------------- | ------------------------ | ------------ |
| 新闻列表管理API  | 无法查看和管理入库的新闻 | 立即         |
| 新闻管理前端页面 | 用户无法管理知识库内容   | 立即         |
| 历史记录API      | 无法查看问答历史         | 尽快         |
| 历史记录前端页面 | 用户体验不完整           | 尽快         |

### P1 - 功能完整性

| 功能             | 影响                   | 建议完成时间 |
| ---------------- | ---------------------- | ------------ |
| Token刷新        | 登录24小时后需重新登录 | 本周         |
| 密码重置         | 用户忘记密码无法找回   | 本周         |
| Excel上传        | 不支持批量导入Excel    | 本周         |
| 聚类分析真实向量 | 聚类结果不准确         | 本周         |

### P2 - 增强功能

| 功能            | 影响               | 建议完成时间 |
| --------------- | ------------------ | ------------ |
| 百度搜索API集成 | 回退搜索仅模拟数据 | 下周         |
| 邮件通知        | 无法接收入库通知   | 下周         |
| n8n工作流配置   | 无法自动采集新闻   | 下周         |
| 报告导出        | 无法导出分析报告   | 下周         |

### P3 - 优化功能

| 功能           | 影响                   | 建议完成时间 |
| -------------- | ---------------------- | ------------ |
| 关键词趋势分析 | 无法查看关键词变化趋势 | 后续         |
| 用户反馈功能   | 无法收集用户反馈       | 后续         |
| 个人中心页面   | 用户无法修改个人信息   | 后续         |

---

## 8. 总结

### 已完成功能（60%）

1. **用户认证**: 注册、登录、账户锁定 ✅
2. **新闻入库**: 结构化/非结构化数据入库 ✅
3. **RAG问答**: 语义检索+LLM推理 ✅
4. **回退搜索**: 框架已实现，待接入真实API ⚠️
5. **关键词统计**: TF-IDF Top10 ✅
6. **聚类分析**: 框架已实现，使用随机向量 ⚠️

### 待实现功能（40%）

1. **内容管理**: 新闻CRUD（缺失）
2. **历史记录**: 查询历史展示（缺失）
3. **邮件通知**: 入库通知（缺失）
4. **n8n集成**: 工作流配置（缺失）
5. **百度API**: 真实搜索（缺失）
6. **报告导出**: PDF/CSV导出（缺失）

### 建议下一步工作

1. **首先实现新闻管理API和前端页面** - 这是最核心的缺失功能
2. **完善回退搜索的百度API集成** - 需要申请API Key
3. **配置n8n工作流** - 启动n8n服务并导入工作流
4. **实现邮件通知功能** - 配置SMTP服务

---

**文档状态**: ✅ 待评审  
**最后更新**: 2026-07-11
