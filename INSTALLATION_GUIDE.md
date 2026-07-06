# XU-News-AI-RAG 完整安装指南

## 🎯 目标

本指南帮助你从零开始搭建完整的 XU-News-AI-RAG 系统，包括：

- ✅ 后端 Flask API
- ✅ 前端 React 应用
- ✅ Ollama LLM 服务
- ✅ n8n 工作流（可选）

**预计时间**：30-60 分钟（取决于网速）

---

## 📋 前置要求

### 必需软件

- [x] **Python 3.11+** - [下载](https://www.python.org/downloads/)
- [x] **Node.js 18+** - [下载](https://nodejs.org/)
- [x] **Ollama** - [下载](https://ollama.ai/download)
- [x] **Git** - [下载](https://git-scm.com/)

### 硬件要求

- CPU: 4 核及以上
- 内存: 8GB 及以上（Ollama 需要 4GB+）
- 磁盘: 20GB 可用空间

---

## 🚀 第一步：克隆项目

```bash
# 克隆项目（如果还没有）
git clone https://github.com/xxx.git
cd xu-news-ai-rag
```

---

## 🔧 第二步：配置 Ollama

### 2.1 安装 Ollama

**Windows**:

1. 访问 https://ollama.ai/download
2. 下载 Windows 安装包
3. 双击安装

**Linux/Mac**:

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2.2 拉取模型

```bash
# LLM 模型（用于生成答案）
ollama pull qwen2.5:3b

# Embedding 模型（用于向量化，可选）
ollama pull mxbai-embed-large
```

### 2.3 验证 Ollama

```bash
# 检查版本
ollama --version

# 列出模型
ollama list

# 测试生成（PowerShell）
$body = @{model="qwen2.5:3b"; prompt="你好"; stream=$false} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/generate" -Method Post -Body $body -ContentType "application/json"
```

---

## 🐍 第三步：配置后端

### 3.1 创建虚拟环境

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows PowerShell
venv\Scripts\Activate.ps1
# Windows CMD
venv\Scripts\activate.bat
# Linux/Mac
source venv/bin/activate
```

### 3.2 安装依赖

```bash
# 升级 pip
python -m pip install --upgrade pip

# 安装依赖（可能需要 10-20 分钟）
pip install -r requirements.txt

# 验证安装
python scripts/check_deps.py
```

### 3.3 配置环境变量

**Windows PowerShell**:

```powershell
# 临时设置（当前会话）
$env:OLLAMA_HOST = "http://127.0.0.1:11434"
$env:OLLAMA_MODEL = "qwen2.5:3b"
$env:JWT_SECRET_KEY = "xu-news-secret-key-2026"
```

**或创建 .env 文件**:

```bash
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:3b
JWT_SECRET_KEY=xu-news-secret-key-2026
```

### 3.4 初始化数据库

```bash
python -m scripts/init_db
```

**期望输出**:

```
2026-6-30 XX:XX:XX | INFO | 开始初始化数据库...
2026-6-30 XX:XX:XX | INFO | 数据库初始化完成！
```

### 3.5 创建管理员账户

```bash
python -m scripts/create_admin --email admin@xu-news.com --password Admin123
```

**期望输出**:

```
✓ 管理员账户创建成功！
  邮箱: admin@xu-news.com
  用户名: Admin
  密码: Admin123
```

### 3.6 启动后端

```bash
# 确保环境变量已设置
$env:OLLAMA_HOST = "http://127.0.0.1:11434"
$env:OLLAMA_MODEL = "qwen2.5:3b"

# 启动
python app.py
```

**期望输出**:

```
2026-6-30 XX:XX:XX | INFO | 数据库初始化完成
2026-6-30 XX:XX:XX | INFO | XU-News-AI-RAG Backend v1.0.0 启动成功
2026-6-30 XX:XX:XX | INFO | 环境: development
2026-6-30 XX:XX:XX | INFO | Ollama 地址: http://127.0.0.1:11434
 * Running on http://127.0.0.1:5000
```

### 3.7 验证后端

**在新的 PowerShell 窗口**:

```powershell
# 健康检查
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/health"
```

**期望输出**（所有服务 status 为 "up"）:

```json
{
  "status": "healthy",
  "services": {
    "database": { "status": "up" },
    "faiss": { "status": "up", "total_vectors": 0 },
    "ollama": { "status": "up", "model": "qwen2.5:3b" }
  }
}
```

---

## ⚛️ 第四步：配置前端

### 4.1 安装依赖

**在新的终端窗口**:

```bash
cd frontend

# 安装依赖（可能需要 5-10 分钟）
npm install
```

### 4.2 配置环境变量

创建 `.env.local` 文件：

**Windows PowerShell**:

```powershell
@"
VITE_API_BASE_URL=http://localhost:5000
"@ | Out-File -Encoding UTF8 .env.local
```

**Linux/Mac**:

```bash
cat > .env.local << EOF
VITE_API_BASE_URL=http://localhost:5000
EOF
```

### 4.3 启动前端

```bash
npm run dev
```

**期望输出**:

```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### 4.4 访问前端

浏览器打开：http://localhost:3000

---

## 🎉 第五步：测试完整流程

### 5.1 注册账户

1. 访问 http://localhost:3000/register
2. 输入邮箱、密码（至少 8 位，包含字母和数字）
3. 点击注册

### 5.2 登录

1. 使用刚才的邮箱密码登录
2. 成功后跳转到仪表盘

### 5.3 入库测试数据

访问 http://localhost:3000/ingest

在 JSON 输入框中粘贴：

```json
[
  {
    "title": "OpenAI 发布 GPT-5",
    "content": "OpenAI 今日宣布发布最新一代语言模型 GPT-5，性能相比 GPT-4 大幅提升。新模型在多个基准测试中刷新了记录，特别是在代码生成和多语言理解方面表现出色。GPT-5 采用了全新的训练方法，大幅降低了计算成本，同时提升了模型的推理能力。业界专家认为，GPT-5 的发布标志着人工智能进入了新的发展阶段。",
    "url": "https://example.com/news/gpt5-release",
    "source": "科技日报",
    "category": "科技",
    "published_at": "2026-6-30T10:00:00Z"
  },
  {
    "title": "人工智能技术在医疗领域的应用",
    "content": "近年来，人工智能技术在医疗领域取得了显著进展。AI 辅助诊断系统可以帮助医生更准确地识别疾病，大幅提高诊断效率。深度学习算法在医学影像分析、药物研发、个性化治疗等方面展现出巨大潜力。据统计，AI 医疗应用的准确率已经接近甚至超过人类专家水平。",
    "url": "https://example.com/news/ai-healthcare",
    "source": "医学新闻",
    "category": "医疗",
    "published_at": "2025-10-08T15:00:00Z"
  }
]
```

点击"开始入库"，等待完成。

### 5.4 测试 RAG 查询

1. 访问 http://localhost:3000/query
2. 输入问题："最近关于人工智能的新闻有哪些？"
3. 点击"提问"
4. 查看 AI 答案和引用来源

### 5.5 查看报告

1. 访问 http://localhost:3000/reports
2. 选择"关键词 Top10"
3. 查看统计图表

---

## 📊 系统架构（运行时）

```
终端 1: Flask Backend (http://localhost:5000)
  ├── SQLite 数据库
  ├── FAISS 向量索引
  └── 调用 Ollama API

终端 2: Ollama Service (http://localhost:11434)
  └── qwen2.5:3b 模型

终端 3: React Frontend (http://localhost:3000)
  └── 调用 Flask API
```

---

## 🐛 常见问题

### Q1: 后端 Ollama 状态为 "down"

**解决步骤**：

```powershell
# 1. 检查环境变量
$env:OLLAMA_HOST

# 2. 修正环境变量（如果是 0.0.0.0）
$env:OLLAMA_HOST = "http://127.0.0.1:11434"

# 3. 重启 Flask
# 在 Flask 终端按 Ctrl+C，然后重新运行 python app.py
```

### Q2: 依赖安装失败

```bash
# 使用国内镜像（中国用户）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用极简版
pip install -r requirements-minimal.txt
```

### Q3: 前端无法连接后端

```bash
# 检查 .env.local
cat .env.local

# 确保内容为
VITE_API_BASE_URL=http://localhost:5000

# 重启前端（Ctrl+C 后重新 npm run dev）
```

### Q4: RAG 查询返回"未找到相关内容"

**原因**：FAISS 索引为空（还没有入库数据）

**解决**：先在"数据入库"页面上传测试数据

---

## ✅ 验证清单

- [ ] Ollama 已安装并拉取模型
- [ ] 后端依赖安装成功（`python scripts/check_deps.py` 通过）
- [ ] 数据库已初始化
- [ ] 管理员账户已创建
- [ ] 后端启动成功（端口 5000）
- [ ] 健康检查返回 "healthy"
- [ ] 前端依赖安装成功
- [ ] 前端启动成功（端口 3000）
- [ ] 可以注册/登录
- [ ] 可以入库数据
- [ ] 可以 RAG 查询

---

## 🎓 下一步

完成安装后，建议：

1. **阅读文档**：
   - `docs/PRD.md` - 了解产品需求
   - `docs/ARCHITECTURE.md` - 了解系统架构
   - `docs/API_SPEC.md` - 了解 API 规范

2. **测试功能**：
   - 入库更多测试数据
   - 尝试不同的查询问题
   - 查看聚类分析报告

3. **配置 n8n**（可选）：
   - 启动 n8n: `npx n8n`
   - 导入工作流: `workflows/news_crawler_workflow.json`
   - 配置自动化爬取

---

**安装完成！** 🎉

如有问题，请参考：

- `backend/QUICKSTART.md`
- `frontend/QUICKSTART.md`
- `docs/OPS_GUIDE.md`
