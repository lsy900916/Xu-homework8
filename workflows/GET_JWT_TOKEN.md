# 如何获取 JWT Token（用于 n8n 配置）

## 方法 1: 从浏览器获取（推荐）

### 步骤 1: 登录前端

访问 http://localhost:5173 并登录

### 步骤 2: 打开开发者工具

按 **F12** 或右键 → "检查"

### 步骤 3: 查看 Local Storage

1. 切换到 **"Application"** 标签（Chrome）或 **"存储"** 标签（Firefox）
2. 左侧展开 **"Local Storage"**
3. 点击 **"http://localhost:5173"**
4. 找到键 **`xu_news_token`**
5. **复制它的值**（类似 `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`）

### 步骤 4: 粘贴到 n8n

在 n8n 工作流变量 `JWT_TOKEN` 中粘贴这个值

---

## 方法 2: 使用 PowerShell 获取（命令行）

```powershell
# 调用登录 API
$loginData = @{
    email = "test3@example.com"  # 你的邮箱
    password = "Aa123456"         # 你的密码
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -Body $loginData -ContentType "application/json"

# 显示 Token
$response.data.token
```

**复制输出的 Token**

---

## 方法 3: 使用 curl（Git Bash 或 WSL）

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test3@example.com","password":"Aa123456"}' \
  | jq -r '.data.token'
```

---

## ⚠️ 注意事项

### Token 有效期

- JWT Token **有效期 24 小时**
- 过期后需要重新获取
- 建议在 n8n 中使用长期有效的 API Key（待后端实现）

### 安全建议

- ❌ 不要将 Token 提交到 Git
- ❌ 不要在公开文档中暴露 Token
- ✅ Token 过期后及时更新 n8n 配置

---

## 🎯 配置示例

在 n8n Workflow Settings → Variables 中：

```
JWT_TOKEN = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MzUwNDY4MDB9.abc123...
```

（这是示例，实际 Token 会更长）

---

## ✅ 验证 Token 是否有效

```powershell
# 设置变量
$token = "你复制的Token"

# 测试
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/me" -Headers $headers
```

**成功输出**：
```json
{
  "code": 0,
  "data": {
    "user_id": 1,
    "email": "test3@example.com",
    ...
  }
}
```

**失败输出**：
```
401 Unauthorized - Token 无效或过期
```

