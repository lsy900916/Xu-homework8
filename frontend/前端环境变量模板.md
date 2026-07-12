# 前端环境变量配置

## 📝 创建 .env.local 文件

将以下内容保存为 `frontend/.env.local`：

```bash
# ==================== API 配置 ====================
# 后端 API 地址
VITE_API_BASE_URL=http://localhost:5000

# ==================== 应用配置 ====================
# 应用标题
VITE_APP_TITLE=XU-News AI-RAG

# 应用版本
VITE_APP_VERSION=1.0.0

# ==================== 功能配置 ====================
# 默认分页大小
VITE_PAGE_SIZE=20

# ==================== 开发配置 ====================
# 是否显示调试信息
VITE_DEBUG=true
```

## 🚀 快速创建命令

### Windows PowerShell
```powershell
@"
VITE_API_BASE_URL=http://localhost:5000
VITE_APP_TITLE=XU-News AI-RAG
VITE_PAGE_SIZE=20
"@ | Out-File -Encoding UTF8 .env.local
```

### Linux/Mac
```bash
cat > .env.local << 'EOF'
VITE_API_BASE_URL=http://localhost:5000
VITE_APP_TITLE=XU-News AI-RAG
VITE_PAGE_SIZE=20
EOF
```

## 📖 配置说明

### VITE_API_BASE_URL

后端 API 的基础地址。

- **开发环境**：`http://localhost:5000`
- **生产环境**：`https://api.xu-news.com`

### 如何使用

在代码中通过 `import.meta.env` 访问：

```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL
console.log(apiUrl) // http://localhost:5000
```

## ⚠️ 注意事项

1. **.env.local 不会被提交到 Git**（已在 .gitignore 中）
2. **修改环境变量后需要重启开发服务器**
3. **所有环境变量必须以 `VITE_` 开头**才能在前端访问

