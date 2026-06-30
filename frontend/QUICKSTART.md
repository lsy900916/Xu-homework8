# Frontend 快速启动指南

## 🚀 5 分钟快速开始

### 步骤 1: 安装依赖

```bash
cd frontend
npm install
```

### 步骤 2: 配置环境变量

创建 `.env.local` 文件：

```bash
# Windows PowerShell
@"
VITE_API_BASE_URL=http://localhost:5000
"@ | Out-File -Encoding UTF8 .env.local

# Linux/Mac
cat > .env.local << EOF
VITE_API_BASE_URL=http://localhost:5000
EOF
```

### 步骤 3: 启动开发服务器

```bash
npm run dev
```

浏览器访问：http://localhost:3000

### 步骤 4: 登录测试

1. 点击"立即注册"创建账户
2. 输入邮箱和密码（密码至少 8 位，包含字母和数字）
3. 注册成功后登录
4. 进入仪表盘

## 📸 页面预览

### 1. 登录页 (http://localhost:3000/login)
- 邮箱 + 密码登录
- JWT Token 自动管理
- 链接到注册页

### 2. 仪表盘 (http://localhost:3000/dashboard)
- 系统状态监控
- 数据库、FAISS、Ollama 状态
- 快速操作入口

### 3. 查询页 (http://localhost:3000/query)
- 输入问题
- 查看 AI 答案
- 查看引用来源

### 4. 入库页 (http://localhost:3000/ingest)
- JSON 批量入库
- 文本/HTML 入库
- 入库结果展示

### 5. 报告页 (http://localhost:3000/reports)
- 关键词 Top10（柱状图）
- 聚类分析
- 时间范围筛选

### 6. 设置页 (http://localhost:3000/settings)
- Ollama 配置
- 回退搜索开关
- SMTP 配置

## 🧪 测试前端

### 测试注册登录流程

```bash
# 打开浏览器控制台（F12）

# 1. 访问注册页
http://localhost:3000/register

# 2. 填写表单
邮箱: test@example.com
密码: Test1234
确认密码: Test1234

# 3. 点击注册

# 4. 跳转到登录页，输入刚才的邮箱密码

# 5. 登录成功，跳转到仪表盘
```

### 测试 RAG 查询

前提：后端已启动，并且已入库一些测试数据

```bash
# 1. 访问查询页
http://localhost:3000/query

# 2. 输入问题
最近关于 AI 的新闻有哪些？

# 3. 点击提问

# 4. 查看答案和引用来源
```

## 🔧 开发技巧

### 查看网络请求

打开浏览器开发者工具（F12） → Network 标签页

### 查看本地存储

开发者工具 → Application → Local Storage

应该看到：
- `xu_news_token` - JWT Token
- `xu_news_user` - 用户信息
- `xu-news-settings` - 设置（Zustand persist）

### 热重载

修改代码后自动刷新，无需手动重启

## 🐛 常见问题

### Q1: npm install 失败

```bash
# 清理缓存
npm cache clean --force

# 删除 node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### Q2: 端口 3000 被占用

```bash
# 方法 1: 修改端口（vite.config.ts）
server: {
  port: 3001
}

# 方法 2: 杀死占用进程
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill
```

### Q3: API 请求失败（CORS 错误）

检查：
1. 后端是否启动（http://localhost:5000）
2. `.env.local` 中的 `VITE_API_BASE_URL` 是否正确
3. 后端 CORS 配置是否包含前端地址

### Q4: 样式不显示

```bash
# 重新构建 Tailwind
npm run build

# 或重启开发服务器
# Ctrl+C 停止，然后
npm run dev
```

## 📦 构建部署

```bash
# 构建生产版本
npm run build

# 输出目录: dist/

# 预览构建结果
npm run preview

# 部署到 Nginx
cp -r dist/* /var/www/html/
```

## 🔗 相关资源

- [Vite 文档](https://vitejs.dev/)
- [React Router 文档](https://reactrouter.com/)
- [TanStack Query 文档](https://tanstack.com/query)
- [TailwindCSS 文档](https://tailwindcss.com/)

