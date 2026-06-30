# 🎯 XU-News-AI-RAG 最终安装步骤

## 当前状态诊断

根据之前的输出：

- ✅ Ollama 已安装并运行（端口 11434）
- ✅ 模型已拉取（qwen2.5:3b, mxbai-embed-large）
- ✅ 后端依赖已安装
- ✅ 数据库已初始化
- ⚠️ Ollama 连接问题（环境变量配置为 0.0.0.0）

---

## 🔧 立即修复并完成安装

### 步骤 1: 修复后端环境变量（已修复 ✅）

**在后端运行的 PowerShell 终端**：

```powershell
# 1. 停止 Flask（按 Ctrl+C）

# 2. 设置正确的环境变量
$env:OLLAMA_HOST = "http://127.0.0.1:11434"
$env:OLLAMA_MODEL = "qwen2.5:3b"
$env:JWT_SECRET_KEY = "xu-news-secret-key-2026"

# 3. 重启 Flask
cd E:\XU-News-AI-RAG\backend
venv\Scripts\Activate.ps1
python app.py
```

**期望看到**：

```
2026-6-30 XX:XX:XX | INFO | Ollama 地址: http://127.0.0.1:11434
 * Running on http://127.0.0.1:5000
```

---

### 步骤 2: 验证后端健康（新 PowerShell 窗口）

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/health"
```

**期望输出**：

```json
{
  "status": "healthy",
  "services": {
    "ollama": { "status": "up" }
  }
}
```

如果还是 "down"，运行：

```powershell
cd E:\XU-News-AI-RAG\backend
python scripts/test_health.py
```

把完整输出发给我。

---

### 步骤 3: 安装前端依赖

**在新的 PowerShell 窗口**：

```powershell
cd E:\XU-News-AI-RAG\frontend
npm install
```

**预计时间**：5-10 分钟

**期望输出**：

```
added XXX packages in XXm
```

---

### 步骤 4: 配置前端环境变量

```powershell
# 创建 .env.local
@"
VITE_API_BASE_URL=http://localhost:5000
"@ | Out-File -Encoding UTF8 .env.local

# 验证
Get-Content .env.local
```

**应该看到**：

```
VITE_API_BASE_URL=http://localhost:5000
```

---

### 步骤 5: 启动前端

```powershell
npm run dev
```

**期望输出**：

```
  VITE v5.0.8  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  press h to show help
```

---

### 步骤 6: 访问前端并测试

1. **打开浏览器**：http://localhost:3000

2. **注册账户**：
   - 点击"立即注册"
   - 邮箱：test@example.com
   - 密码：Test1234
   - 点击注册

3. **登录**：
   - 使用刚才的邮箱密码登录
   - 成功后进入仪表盘

4. **检查系统状态**：
   - 仪表盘应显示所有服务为"正常"
   - FAISS 向量数为 0（还没有数据）

5. **入库测试数据**：
   - 访问"数据入库"页面
   - 切换到"结构化数据（JSON）"标签
   - 粘贴测试数据（见下方）
   - 点击"开始入库"

**测试 JSON 数据**：

```json
[
  {
    "title": "OpenAI 发布 GPT-5",
    "content": "OpenAI 今日宣布发布最新一代语言模型 GPT-5，性能相比 GPT-4 大幅提升。新模型在多个基准测试中刷新了记录，特别是在代码生成和多语言理解方面表现出色。GPT-5 采用了全新的训练方法，大幅降低了计算成本，同时提升了模型的推理能力。业界专家认为，GPT-5 的发布标志着人工智能进入了新的发展阶段。",
    "url": "https://example.com/news/gpt5",
    "source": "科技日报",
    "category": "科技"
  },
  {
    "title": "AI 在医疗领域的突破",
    "content": "人工智能技术在医疗领域取得了重大突破。最新研究表明，AI 辅助诊断系统在多种疾病的识别准确率上已经超过人类医生的平均水平。深度学习算法可以从医学影像中快速识别病灶，大幅提高诊断效率。此外，AI 还在药物研发、个性化治疗方案制定等方面发挥重要作用。",
    "url": "https://example.com/news/ai-medical",
    "source": "医学周刊",
    "category": "医疗"
  }
]
```

6. **测试 RAG 查询**：
   - 访问"知识库查询"页面
   - 输入："最近关于人工智能的新闻有哪些？"
   - 点击"提问"
   - 查看 AI 答案和引用来源

7. **查看报告**：
   - 访问"分析报告"页面
   - 查看关键词 Top10

---

## 🎉 完成标志

当你看到以下内容时，说明安装完全成功：

1. ✅ 仪表盘显示所有服务状态为"正常"或"up"
2. ✅ FAISS 向量数 > 0（入库后）
3. ✅ RAG 查询能返回答案和引用来源
4. ✅ 报告页面显示关键词统计

---

## 🐛 如果遇到问题

### 问题排查优先级

1. **后端 Ollama 状态 "down"**
   - 运行：`python scripts/test_health.py`
   - 检查：环境变量 `$env:OLLAMA_HOST`
   - 修复：确保是 `http://127.0.0.1:11434`

2. **前端无法登录**
   - 检查：后端是否运行（http://localhost:5000/api/health）
   - 检查：`.env.local` 配置
   - 查看：浏览器控制台（F12）Network 标签

3. **入库失败**
   - 检查：FAISS 索引目录是否存在
   - 检查：Embedding 模型是否加载成功
   - 查看：后端日志 `logs/app.log`

---

## 📞 需要帮助？

如果按照步骤操作后仍有问题，请提供：

1. `python scripts/test_health.py` 的完整输出
2. 后端启动日志（前 20 行）
3. 浏览器控制台的错误信息（如果有）

---

**祝你成功！** 🎊
