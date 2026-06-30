/**
 * 仪表盘页面 - 今日统计
 */
import { useQuery } from "@tanstack/react-query";
import { systemAPI } from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";
import { Activity, Database, MessageSquare, AlertCircle } from "lucide-react";

export default function Dashboard() {
  const { data: health, isLoading } = useQuery({
    queryKey: ["health"],
    queryFn: systemAPI.getHealth,
    refetchInterval: 10000, // 每 10 秒刷新
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner text="加载中..." />
      </div>
    );
  }

  const statusColor = (status) => {
    switch (status) {
      case "up":
      case "healthy":
        return "text-green-600 bg-green-50";
      case "down":
        return "text-red-600 bg-red-50";
      default:
        return "text-yellow-600 bg-yellow-50";
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">仪表盘</h1>
        <p className="text-gray-600 mt-2">系统运行状态与统计</p>
      </div>

      {/* 系统状态卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* 数据库状态 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">数据库</p>
              <p
                className={`text-lg font-semibold mt-1 ${statusColor(health?.services.database.status || "down")}`}
              >
                {health?.services.database.status === "up" ? "正常" : "异常"}
              </p>
            </div>
            <div className="p-3 bg-blue-50 rounded-full">
              <Database className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        {/* FAISS 状态 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">向量索引</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {health?.services.faiss.total_vectors || 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">向量数</p>
            </div>
            <div className="p-3 bg-purple-50 rounded-full">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Ollama 状态 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Ollama</p>
              <p
                className={`text-lg font-semibold mt-1 ${statusColor(health?.services.ollama.status || "down")}`}
              >
                {health?.services.ollama.status === "up" ? "正常" : "离线"}
              </p>
              {health?.services.ollama.model && (
                <p className="text-xs text-gray-500 mt-1">
                  {health.services.ollama.model}
                </p>
              )}
            </div>
            <div className="p-3 bg-green-50 rounded-full">
              <MessageSquare className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        {/* 系统状态 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">系统状态</p>
              <p
                className={`text-lg font-semibold mt-1 ${statusColor(health?.status || "degraded")}`}
              >
                {health?.status === "healthy" ? "健康" : "降级"}
              </p>
              <p className="text-xs text-gray-500 mt-1">v{health?.version}</p>
            </div>
            <div
              className={`p-3 rounded-full ${health?.status === "healthy" ? "bg-green-50" : "bg-yellow-50"}`}
            >
              <AlertCircle
                className={`w-6 h-6 ${health?.status === "healthy" ? "text-green-600" : "text-yellow-600"}`}
              />
            </div>
          </div>
        </div>
      </div>

      {/* 详细服务状态 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">服务详情</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="font-medium text-gray-900">数据库</p>
              <p className="text-sm text-gray-600">SQLite</p>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${statusColor(health?.services.database.status || "down")}`}
            >
              {health?.services.database.status || "unknown"}
            </span>
          </div>

          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="font-medium text-gray-900">FAISS 向量存储</p>
              <p className="text-sm text-gray-600">
                已存储 {health?.services.faiss.total_vectors || 0} 个向量
              </p>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${statusColor(health?.services.faiss.status || "down")}`}
            >
              {health?.services.faiss.status || "unknown"}
            </span>
          </div>

          <div className="flex items-center justify-between py-3">
            <div>
              <p className="font-medium text-gray-900">Ollama LLM</p>
              <p className="text-sm text-gray-600">
                {health?.services.ollama.model || "未配置"} @{" "}
                {health?.services.ollama.host || "N/A"}
              </p>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${statusColor(health?.services.ollama.status || "down")}`}
            >
              {health?.services.ollama.status || "unknown"}
            </span>
          </div>
        </div>
      </div>

      {/* 快速操作 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">快速开始</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/query"
            className="block p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
          >
            <MessageSquare className="w-8 h-8 text-primary-600 mx-auto mb-2" />
            <p className="font-medium text-gray-900">开始提问</p>
            <p className="text-sm text-gray-600 mt-1">使用 RAG 查询新闻</p>
          </a>

          <a
            href="/ingest"
            className="block p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
          >
            <Database className="w-8 h-8 text-primary-600 mx-auto mb-2" />
            <p className="font-medium text-gray-900">数据入库</p>
            <p className="text-sm text-gray-600 mt-1">上传新闻数据</p>
          </a>

          <a
            href="/reports"
            className="block p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
          >
            <Activity className="w-8 h-8 text-primary-600 mx-auto mb-2" />
            <p className="font-medium text-gray-900">查看报告</p>
            <p className="text-sm text-gray-600 mt-1">聚类与关键词分析</p>
          </a>
        </div>
      </div>
    </div>
  );
}
