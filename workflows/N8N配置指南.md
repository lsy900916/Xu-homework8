# n8n 工作流配置完整指南

## 🎯 配置位置：在 n8n Web 界面中

---

## 📋 第一步：启动 n8n

```powershell
# 在新的 PowerShell 窗口
npx n8n
```

访问：**http://localhost:5678**

---

## 📥 第二步：导入工作流

1. 在 n8n 界面左上角，点击 **"工作流" 或 "Workflows"** 下拉菜单
2. 选择 **"导入" 或 "Import"**
3. 点击 **"从文件" 或 "From File"**
4. 选择文件：`E:\XU-News-AI-RAG\workflows\news_ingest_notify.json`
5. 点击 **"导入" 或 "Import"**

✅ 工作流已导入！你会看到完整的节点流程图。

---

## ⚙️ 第三步：配置工作流变量

### 3.1 打开设置面板

在工作流编辑界面：

1. 点击右上角 **齿轮图标 ⚙️** 或 **"Settings"**
2. 或者点击 **"Workflow" → "Settings"**

### 3.2 找到变量配置

在设置面板中：

1. 向下滚动找到 **"Variables"** 或 **"工作流变量"** 部分
2. 你会看到 6 个预定义的变量

### 3.3 填写变量值

| 变量名 | 需要填写的值 | 如何获取 |
|-------|------------|---------|
| **BACKEND_BASE_URL** | `http://localhost:5000` | 保持默认即可 |
| **JWT_TOKEN** | `eyJhbGci...`（很长） | 👇 见下方详细步骤 |
| **SOURCES** | `https://news.example.com/rss` | 任何有效的 RSS 源 |
| **SOURCE_NAME** | `示例新闻` | 自定义来源名称 |
| **SMTP_USER** | `123456789@qq.com` | 你的 QQ 邮箱 |
| **EMAIL_TO** | `recipient@qq.com` | 接收日报的邮箱 |

---

## 🔑 获取 JWT_TOKEN（重点！）

### 方式 A: 从浏览器复制（最简单）

1. **登录前端**：http://localhost:5173
2. **按 F12** 打开开发者工具
3. **切换到 "Application" 标签**（Chrome）或 "存储" 标签（Edge/Firefox）
4. **左侧展开 "Local Storage"**
5. **点击 "http://localhost:5173"**
6. **右侧找到 `xu_news_token` 这一行**
7. **双击值的部分，Ctrl+C 复制**

![示例图]
```
Key                  | Value
---------------------|----------------------------------------
xu_news_token        | eyJhbGciOiJIUzI1NiIsInR5cCI6Ik... (复制这个)
xu_news_user         | {"user_id":1,"email":...}
```

8. **粘贴到 n8n 的 JWT_TOKEN 变量中**

---

### 方式 B: 用 PowerShell 获取

```powershell
# 替换为你的实际邮箱密码
$loginData = @{
    email = "test3@example.com"
    password = "Aa123456"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -Body $loginData -ContentType "application/json"

# 显示 Token（复制这个）
Write-Host "JWT Token:" -ForegroundColor Green
$response.data.token
```

**复制输出的 Token 到 n8n**

---

## 📧 第四步：配置 QQ SMTP 凭据

### 4.1 获取 QQ 邮箱授权码

1. 登录 **QQ 邮箱网页版**：https://mail.qq.com
2. 点击 **"设置" → "账户"**
3. 向下滚动到 **"POP3/IMAP/SMTP 服务"**
4. 开启 **"IMAP/SMTP 服务"**
5. 点击 **"生成授权码"**（需要短信验证）
6. **复制授权码**（16 位，如 `abcdefghijklmnop`）

### 4.2 在 n8n 中添加 SMTP 凭据

1. 在 n8n 界面，点击右上角 **"Credentials"** 或 **"凭据"**
2. 点击 **"Add Credential"** 或 **"新建凭据"**
3. 搜索并选择 **"SMTP"**
4. 填写：
   ```
   Name: QQ SMTP Credentials
   Host: smtp.qq.com
   Port: 465
   User: 你的QQ邮箱（如 123456789@qq.com）
   Password: QQ邮箱授权码（16位，非登录密码）
   SSL/TLS: 启用（打勾）
   ```
5. 点击 **"Save"** 或 **"保存"**

### 4.3 关联到工作流节点

1. 在工作流中，点击 **"Email-发送日报邮件"** 节点
2. 在 **"Credentials"** 下拉框中
3. 选择刚才创建的 **"QQ SMTP Credentials"**

---

## ✅ 第五步：测试工作流

1. 点击右上角 **"Test Workflow"** 或 **"测试执行"** 按钮
2. 观察每个节点的执行情况
3. 如果某个节点失败，点击查看错误详情

---

## 🎯 快速配置清单（复制使用）

在 n8n **Workflow Settings → Variables** 中配置：

```javascript
// 必须配置
BACKEND_BASE_URL = http://localhost:5000
JWT_TOKEN = (从浏览器 F12 → Application → Local Storage → xu_news_token 复制)

// RSS 源配置
SOURCES = https://example.com/rss
SOURCE_NAME = 示例新闻网

// 邮件配置
SMTP_USER = 你的QQ邮箱@qq.com
EMAIL_TO = 接收邮件的邮箱@qq.com
```

---

## 📸 配置位置图示（文字版）

```
n8n 界面布局:
┌──────────────────────────────────────┐
│  [工作流名称]         [Settings ⚙️] │  ← 点击这里
├──────────────────────────────────────┤
│                                      │
│  设置面板                             │
│  ├─ General                          │
│  ├─ Error Workflow                   │
│  ├─ Timezone                         │
│  └─ Variables  ← 在这里配置变量       │
│     ├─ BACKEND_BASE_URL              │
│     ├─ JWT_TOKEN                     │
│     ├─ SOURCES                       │
│     ├─ SOURCE_NAME                   │
│     ├─ SMTP_USER                     │
│     └─ EMAIL_TO                      │
└──────────────────────────────────────┘
```

---

## 🐛 常见问题

### Q1: 找不到 Variables 选项

**可能原因**：n8n 版本不同

**解决**：
- 在每个节点中直接修改参数（找到 `{{ $workflow.settings.XXX }}` 的地方，替换为实际值）

### Q2: SMTP 连接失败

**检查**：
1. QQ 邮箱是否开启 SMTP 服务
2. 授权码是否正确（16 位）
3. 端口选择 465（SSL）
4. 网络是否允许连接 smtp.qq.com

### Q3: JWT Token 无效

**原因**：Token 过期（24 小时）

**解决**：重新登录获取新 Token

---

## 📝 完整配置示例

```javascript
// === 复制以下内容，修改后填入 n8n ===

BACKEND_BASE_URL = http://localhost:5000

JWT_TOKEN = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MzUwNDY4MDB9.abc123xyz...

SOURCES = https://example.com/rss,https://news.org/feed

SOURCE_NAME = 示例新闻网

SMTP_USER = your-email@qq.com

EMAIL_TO = recipient@qq.com
```

---

现在你知道在哪配置了！需要我继续解释哪个部分吗？

