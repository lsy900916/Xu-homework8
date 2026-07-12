# XU-News-AI-RAG Workflows

n8n 工作流配置文件

## 工作流列表
- `news_crawler_workflow.json` - 新闻爬虫工作流
- `schedule_crawler_workflow.json` - 定时爬取工作流
- `data_processing_workflow.json` - 数据处理工作流

## 导入方式
1. 启动 n8n: `npx n8n`
2. 访问 http://localhost:5678
3. 导入对应的 JSON 文件

## 环境变量
需要在 n8n 中配置：
- Backend API Endpoint
- 认证凭据

