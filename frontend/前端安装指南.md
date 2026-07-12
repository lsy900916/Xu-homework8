# Frontend 完整安装步骤（Windows PowerShell）

## 📍 当前位置

```powershell
cd E:\XU-News-AI-RAG\frontend
```

---

## 步骤 1️⃣: 安装依赖

```powershell
npm install
```

**等待安装完成**（5-10 分钟）

输出应类似：
```
added 500+ packages in 5m
```

---

## 步骤 2️⃣: 创建配置文件

```powershell
@"
VITE_API_BASE_URL=http://localhost:5000
"@ | Out-File -Encoding UTF8 .env.local
```

验证：
```powershell
Get-Content .env.local
```

应显示：
```
VITE_API_BASE_URL=http://localhost:5000
```

---

## 步骤 3️⃣: 启动开发服务器

```powershell
npm run dev
```

**期望输出**：
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

---

## 步骤 4️⃣: 打开浏览器

访问：**http://localhost:3000**

应该看到登录页面。

---

## 步骤 5️⃣: 注册并登录

1. 点击"立即注册"
2. 填写：
   - 邮箱：test@example.com
   - 密码：Test1234（至少 8 位，字母+数字）
   - 确认密码：Test1234
3. 点击"注册"
4. 自动跳转到登录页
5. 使用刚才的邮箱密码登录
6. 进入仪表盘

---

## 步骤 6️⃣: 入库测试数据

1. 点击左侧"数据入库"
2. 在 JSON 输入框粘贴：

```json
[
  {
    "title": "OpenAI 发布 GPT-5",
    "content": "OpenAI 今日宣布发布最新一代语言模型 GPT-5，性能相比 GPT-4 大幅提升。新模型在多个基准测试中刷新了记录，特别是在代码生成和多语言理解方面表现出色。GPT-5 采用了全新的训练方法，大幅降低了计算成本，同时提升了模型的推理能力。业界专家认为，GPT-5 的发布标志着人工智能进入了新的发展阶段。这一突破性进展将推动 AI 技术在各个领域的广泛应用。",
    "url": "https://example.com/news/gpt5-2025",
    "source": "科技日报",
    "category": "科技"
  }
]
```

3. 点击"开始入库"
4. 等待完成（可能需要 10-30 秒，因为要向量化）

**期望结果**：
```
✓ 入库完成！成功 1 条，失败 0 条
```

---

## 步骤 7️⃣: 测试 RAG 查询

1. 点击左侧"知识库查询"
2. 输入问题："OpenAI 最近发布了什么？"
3. 点击"提问"
4. 等待 5-10 秒

**期望结果**：
- 显示 AI 生成的答案
- 显示引用来源（GPT-5 的新闻）
- 显示统计信息（召回数量、耗时等）

---

## ✅ 成功标志

当你看到以下内容时，说明系统完全正常：

1. ✅ 仪表盘"系统状态"显示"健康"
2. ✅ Ollama 状态显示"正常"
3. ✅ FAISS 向量数 > 0
4. ✅ RAG 查询能返回答案
5. ✅ 答案中包含引用来源

---

## 🎊 恭喜！

你已经成功搭建了完整的 XU-News-AI-RAG 系统！

### 现在你可以：

- 🔍 **查询新闻**：在查询页面提问任何问题
- 📊 **查看统计**：在报告页面查看关键词和聚类
- 📥 **批量入库**：上传 Excel 或 JSON 数据
- ⚙️ **调整设置**：在设置页面配置系统参数

---

## 📚 下一步

### 功能探索

1. **多入库几条数据**，让系统有更多内容可以检索
2. **尝试不同的问题**，测试 RAG 的效果
3. **查看聚类分析**（需要至少 10+ 条数据）
4. **配置 n8n 工作流**（自动化爬取）

### 深入了解

- 阅读 `docs/ARCHITECTURE.md` 了解系统设计
- 阅读 `docs/API_SPEC.md` 了解 API 细节
- 查看 `backend/core/rag.py` 了解 RAG 实现

---

## 📞 遇到问题？

参考文档：
- `INSTALLATION_GUIDE.md` - 完整安装指南
- `backend/QUICKSTART.md` - 后端快速开始
- `frontend/QUICKSTART.md` - 前端快速开始
- `docs/OPS_GUIDE.md` - 运维指南

或提供以下信息寻求帮助：
1. 健康检查输出
2. 后端启动日志
3. 浏览器控制台错误

