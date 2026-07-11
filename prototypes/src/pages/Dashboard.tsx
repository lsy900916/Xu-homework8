import { useState, useEffect } from "react";
import {
  TrendingUp,
  Database,
  MessageSquare,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  Zap,
} from "lucide-react";
import { Header } from "../components/Layout/Header";

const mockStats = [
  {
    label: "新闻总数",
    value: "12,847",
    change: "+12.5%",
    trend: "up",
    icon: Database,
    color: "bg-blue-500",
  },
  {
    label: "今日新增",
    value: "86",
    change: "+23.1%",
    trend: "up",
    icon: Zap,
    color: "bg-green-500",
  },
  {
    label: "问答次数",
    value: "2,456",
    change: "+8.3%",
    trend: "up",
    icon: MessageSquare,
    color: "bg-purple-500",
  },
  {
    label: "平均响应",
    value: "2.3s",
    change: "-15.2%",
    trend: "down",
    icon: Clock,
    color: "bg-orange-500",
  },
];

const mockRecentNews = [
  {
    id: 1,
    title: "人工智能大模型最新进展：Qwen 2.5发布",
    source: "科技日报",
    time: "10分钟前",
    category: "科技",
  },
  {
    id: 2,
    title: "全球AI投资持续升温，Q2融资达50亿美元",
    source: "财经时报",
    time: "30分钟前",
    category: "财经",
  },
  {
    id: 3,
    title: "RAG技术赋能企业知识库建设",
    source: "人工智能杂志",
    time: "1小时前",
    category: "科技",
  },
  {
    id: 4,
    title: "Ollama推出全新轻量级模型系列",
    source: "开源社区",
    time: "2小时前",
    category: "科技",
  },
  {
    id: 5,
    title: "大数据分析助力新闻推荐系统升级",
    source: "数据周刊",
    time: "3小时前",
    category: "数据",
  },
];

const mockActivity = [
  { time: "09:00", queries: 45, news: 12 },
  { time: "10:00", queries: 68, news: 18 },
  { time: "11:00", queries: 89, news: 25 },
  { time: "12:00", queries: 56, news: 15 },
  { time: "13:00", queries: 72, news: 20 },
  { time: "14:00", queries: 95, news: 28 },
  { time: "15:00", queries: 110, news: 32 },
  { time: "16:00", queries: 88, news: 24 },
];

export default function Dashboard() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  const maxQueries = Math.max(...mockActivity.map((a) => a.queries));
  const maxNews = Math.max(...mockActivity.map((a) => a.news));

  return (
    <div className="flex-1 flex flex-col">
      <Header title="仪表盘" subtitle="系统概览与实时数据" />

      <main className="flex-1 p-6 overflow-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {mockStats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={index}
                className="card p-6 animate-fadeIn"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="flex items-center justify-between">
                  <div
                    className={`w-12 h-12 ${stat.color} rounded-xl flex items-center justify-center`}
                  >
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div
                    className={`flex items-center gap-1 text-sm ${stat.trend === "up" ? "text-green-500" : "text-red-500"}`}
                  >
                    {stat.trend === "up" ? (
                      <ArrowUpRight className="w-4 h-4" />
                    ) : (
                      <ArrowDownRight className="w-4 h-4" />
                    )}
                    {stat.change}
                  </div>
                </div>
                <div className="mt-4">
                  <p className="text-2xl font-bold text-gray-800">
                    {stat.value}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">{stat.label}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 card">
            <div className="card-header flex items-center justify-between">
              <h3 className="font-semibold text-gray-800">实时活动趋势</h3>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 bg-primary-500 rounded-full"></span>
                  <span className="text-sm text-gray-600">问答次数</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 bg-secondary-500 rounded-full"></span>
                  <span className="text-sm text-gray-600">新闻入库</span>
                </div>
              </div>
            </div>
            <div className="card-body">
              {loading ? (
                <div className="h-64 flex items-center justify-center">
                  <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
                </div>
              ) : (
                <div className="h-64 flex items-end justify-between gap-4">
                  {mockActivity.map((item, index) => (
                    <div
                      key={index}
                      className="flex-1 flex flex-col items-center gap-2"
                    >
                      <div className="w-full flex items-end gap-1 h-48">
                        <div
                          className="flex-1 bg-primary-100 rounded-t-md hover:bg-primary-200 transition-colors"
                          style={{
                            height: `${(item.queries / maxQueries) * 100}%`,
                          }}
                        ></div>
                        <div
                          className="flex-1 bg-secondary-100 rounded-t-md hover:bg-secondary-200 transition-colors"
                          style={{ height: `${(item.news / maxNews) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500">{item.time}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header flex items-center justify-between">
              <h3 className="font-semibold text-gray-800">最新新闻</h3>
              <button className="text-sm text-primary-500 hover:text-primary-600">
                查看全部
              </button>
            </div>
            <div className="card-body">
              <div className="space-y-4">
                {mockRecentNews.map((news) => (
                  <div
                    key={news.id}
                    className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    <span className="px-2 py-1 bg-primary-100 text-primary-600 text-xs rounded-full">
                      {news.category}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">
                        {news.title}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-gray-500">
                          {news.source}
                        </span>
                        <span className="text-xs text-gray-400">
                          {news.time}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 card">
          <div className="card-header">
            <h3 className="font-semibold text-gray-800">快速操作</h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <button className="flex flex-col items-center gap-3 p-4 bg-blue-50 hover:bg-blue-100 rounded-xl transition-colors">
                <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center">
                  <Database className="w-6 h-6 text-white" />
                </div>
                <span className="text-sm font-medium text-blue-700">
                  数据入库
                </span>
              </button>
              <button className="flex flex-col items-center gap-3 p-4 bg-green-50 hover:bg-green-100 rounded-xl transition-colors">
                <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <span className="text-sm font-medium text-green-700">
                  智能问答
                </span>
              </button>
              <button className="flex flex-col items-center gap-3 p-4 bg-purple-50 hover:bg-purple-100 rounded-xl transition-colors">
                <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <span className="text-sm font-medium text-purple-700">
                  分析报告
                </span>
              </button>
              <button className="flex flex-col items-center gap-3 p-4 bg-orange-50 hover:bg-orange-100 rounded-xl transition-colors">
                <div className="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center">
                  <Clock className="w-6 h-6 text-white" />
                </div>
                <span className="text-sm font-medium text-orange-700">
                  历史记录
                </span>
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
