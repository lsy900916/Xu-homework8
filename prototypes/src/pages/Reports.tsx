import { useState } from "react";
import {
  BarChart3,
  PieChart,
  TrendingUp,
  Download,
  Calendar,
  Filter,
  Share2,
} from "lucide-react";
import { Header } from "../components/Layout/Header";

const mockClusters = [
  {
    id: 1,
    name: "人工智能",
    count: 342,
    keywords: ["AI", "大模型", "深度学习", "Qwen", "GPT"],
  },
  {
    id: 2,
    name: "金融科技",
    count: 256,
    keywords: ["FinTech", "区块链", "支付", "风控", "数字银行"],
  },
  {
    id: 3,
    name: "数据科学",
    count: 189,
    keywords: ["大数据", "数据分析", "机器学习", "可视化", "预测"],
  },
  {
    id: 4,
    name: "云计算",
    count: 145,
    keywords: ["云服务", "AWS", "Azure", "容器", "Kubernetes"],
  },
  {
    id: 5,
    name: "网络安全",
    count: 128,
    keywords: ["安全", "黑客", "加密", "防护", "漏洞"],
  },
];

const mockKeywords = [
  { rank: 1, keyword: "人工智能", count: 856, trend: "+23%", articles: 342 },
  { rank: 2, keyword: "大模型", count: 623, trend: "+18%", articles: 256 },
  { rank: 3, keyword: "RAG", count: 456, trend: "+45%", articles: 189 },
  { rank: 4, keyword: "数据分析", count: 389, trend: "+12%", articles: 167 },
  { rank: 5, keyword: "云计算", count: 324, trend: "+8%", articles: 145 },
  { rank: 6, keyword: "机器学习", count: 298, trend: "+15%", articles: 134 },
  { rank: 7, keyword: "区块链", count: 267, trend: "-5%", articles: 112 },
  { rank: 8, keyword: "网络安全", count: 245, trend: "+21%", articles: 108 },
  { rank: 9, keyword: "Qwen", count: 212, trend: "+67%", articles: 89 },
  { rank: 10, keyword: "Ollama", count: 189, trend: "+34%", articles: 76 },
];

export default function Reports() {
  const [timeRange, setTimeRange] = useState("weekly");
  const [activeTab, setActiveTab] = useState("clusters");

  const timeRanges = [
    { id: "daily", label: "今日" },
    { id: "weekly", label: "本周" },
    { id: "monthly", label: "本月" },
    { id: "yearly", label: "本年" },
  ];

  const totalNews = mockClusters.reduce((sum, c) => sum + c.count, 0);

  return (
    <div className="flex-1 flex flex-col">
      <Header title="分析报告" subtitle="新闻聚类分析与关键词统计" />

      <main className="flex-1 p-6 overflow-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-gray-500" />
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="input-field"
            >
              {timeRanges.map((range) => (
                <option key={range.id} value={range.id}>
                  {range.label}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <button className="btn-secondary flex items-center gap-2">
              <Filter className="w-4 h-4" />
              筛选
            </button>
            <button className="btn-primary flex items-center gap-2">
              <Download className="w-4 h-4" />
              导出报告
            </button>
          </div>
        </div>

        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={() => setActiveTab("clusters")}
            className={`px-6 py-3 rounded-xl font-medium transition-all ${
              activeTab === "clusters"
                ? "bg-primary-500 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            <BarChart3 className="w-5 h-5 inline-block mr-2" />
            聚类分析
          </button>
          <button
            onClick={() => setActiveTab("keywords")}
            className={`px-6 py-3 rounded-xl font-medium transition-all ${
              activeTab === "keywords"
                ? "bg-primary-500 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            <TrendingUp className="w-5 h-5 inline-block mr-2" />
            关键词统计
          </button>
        </div>

        {activeTab === "clusters" ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 card">
              <div className="card-header">
                <h3 className="font-semibold text-gray-800">新闻主题聚类</h3>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  {mockClusters.map((cluster, index) => {
                    const colors = [
                      "bg-blue-500",
                      "bg-green-500",
                      "bg-purple-500",
                      "bg-orange-500",
                      "bg-red-500",
                    ];
                    const percent = ((cluster.count / totalNews) * 100).toFixed(
                      1,
                    );
                    return (
                      <div
                        key={cluster.id}
                        className="p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div
                              className={`w-3 h-3 ${colors[index % colors.length]} rounded-full`}
                            ></div>
                            <span className="font-medium text-gray-800">
                              {cluster.name}
                            </span>
                          </div>
                          <div className="flex items-center gap-4">
                            <span className="text-sm text-gray-500">
                              {cluster.count} 篇
                            </span>
                            <span className="text-sm font-medium text-gray-800">
                              {percent}%
                            </span>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${colors[index % colors.length]}`}
                            style={{ width: `${percent}%` }}
                          ></div>
                        </div>
                        <div className="flex flex-wrap gap-2 mt-3">
                          {cluster.keywords.map((keyword) => (
                            <span
                              key={keyword}
                              className="px-2 py-1 bg-white text-gray-600 text-xs rounded border border-gray-200"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h3 className="font-semibold text-gray-800">聚类分布</h3>
              </div>
              <div className="card-body">
                <div className="flex items-center justify-center h-64">
                  <div className="relative w-48 h-48">
                    <svg
                      viewBox="0 0 100 100"
                      className="w-full h-full transform -rotate-90"
                    >
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        fill="none"
                        stroke="#e2e8f0"
                        strokeWidth="12"
                      />
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        fill="none"
                        stroke="#3b82f6"
                        strokeWidth="12"
                        strokeDasharray={`${(mockClusters[0].count / totalNews) * 251.2} 251.2`}
                      />
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        fill="none"
                        stroke="#10b981"
                        strokeWidth="12"
                        strokeDasharray={`${(mockClusters[1].count / totalNews) * 251.2} 251.2`}
                        strokeDashoffset={`-${(mockClusters[0].count / totalNews) * 251.2}`}
                      />
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        fill="none"
                        stroke="#8b5cf6"
                        strokeWidth="12"
                        strokeDasharray={`${(mockClusters[2].count / totalNews) * 251.2} 251.2`}
                        strokeDashoffset={`-${((mockClusters[0].count + mockClusters[1].count) / totalNews) * 251.2}`}
                      />
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        fill="none"
                        stroke="#f97316"
                        strokeWidth="12"
                        strokeDasharray={`${(mockClusters[3].count / totalNews) * 251.2} 251.2`}
                        strokeDashoffset={`-${((mockClusters[0].count + mockClusters[1].count + mockClusters[2].count) / totalNews) * 251.2}`}
                      />
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        fill="none"
                        stroke="#ef4444"
                        strokeWidth="12"
                        strokeDasharray={`${(mockClusters[4].count / totalNews) * 251.2} 251.2`}
                        strokeDashoffset={`-${((mockClusters[0].count + mockClusters[1].count + mockClusters[2].count + mockClusters[3].count) / totalNews) * 251.2}`}
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-gray-800">
                          {totalNews}
                        </p>
                        <p className="text-xs text-gray-500">总新闻数</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="mt-4 space-y-2">
                  {mockClusters.map((cluster, index) => {
                    const colors = [
                      "bg-blue-500",
                      "bg-green-500",
                      "bg-purple-500",
                      "bg-orange-500",
                      "bg-red-500",
                    ];
                    return (
                      <div key={cluster.id} className="flex items-center gap-2">
                        <div
                          className={`w-3 h-3 ${colors[index % colors.length]} rounded-full`}
                        ></div>
                        <span className="text-sm text-gray-600 flex-1">
                          {cluster.name}
                        </span>
                        <span className="text-sm font-medium text-gray-800">
                          {cluster.count}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="card">
            <div className="card-header flex items-center justify-between">
              <h3 className="font-semibold text-gray-800">关键词 Top 10</h3>
              <div className="flex items-center gap-2">
                <button className="btn-secondary text-sm flex items-center gap-1">
                  <Share2 className="w-4 h-4" />
                  分享
                </button>
              </div>
            </div>
            <div className="card-body">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        排名
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        关键词
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        出现次数
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        趋势
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        相关文章
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        热度
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {mockKeywords.map((keyword) => (
                      <tr
                        key={keyword.rank}
                        className="hover:bg-gray-50 transition-colors"
                      >
                        <td className="px-6 py-4">
                          <span
                            className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                              keyword.rank === 1
                                ? "bg-yellow-400 text-yellow-900"
                                : keyword.rank === 2
                                  ? "bg-gray-300 text-gray-700"
                                  : keyword.rank === 3
                                    ? "bg-orange-300 text-orange-800"
                                    : "bg-gray-100 text-gray-600"
                            }`}
                          >
                            {keyword.rank}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="font-medium text-gray-800">
                            {keyword.keyword}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-600">
                          {keyword.count.toLocaleString()}
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`text-sm font-medium ${keyword.trend.startsWith("+") ? "text-green-500" : "text-red-500"}`}
                          >
                            {keyword.trend}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-600">
                          {keyword.articles} 篇
                        </td>
                        <td className="px-6 py-4">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div
                              className="h-2 rounded-full bg-gradient-to-r from-green-400 to-blue-500"
                              style={{
                                width: `${Math.min((keyword.count / 856) * 100, 100)}%`,
                              }}
                            ></div>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        <div className="mt-6 card">
          <div className="card-header">
            <h3 className="font-semibold text-gray-800">聚类可视化</h3>
          </div>
          <div className="card-body">
            <div className="h-80 bg-gray-50 rounded-xl flex items-center justify-center">
              <div className="text-center">
                <PieChart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">t-SNE 降维可视化展示区域</p>
                <p className="text-sm text-gray-400 mt-2">
                  显示新闻聚类的二维分布散点图
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
