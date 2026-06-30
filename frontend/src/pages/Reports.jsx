/**
 * 分析报告页面
 */
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { reportAPI } from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";
import EmptyState from "../components/EmptyState";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp, Hash } from "lucide-react";

export default function Reports() {
  const [activeTab, setActiveTab] = useState("keywords");
  const [timeRange, setTimeRange] = useState("daily");

  const {
    data: keywordsData,
    isLoading: loadingKeywords,
    refetch: refetchKeywords,
  } = useQuery({
    queryKey: ["keywords", timeRange],
    queryFn: () => reportAPI.getTopKeywords({ time_range: timeRange }),
    enabled: false, // 禁用自动查询，改为手动触发
  });

  const {
    data: clustersData,
    isLoading: loadingClusters,
    refetch: refetchClusters,
  } = useQuery({
    queryKey: ["clusters"],
    queryFn: () => reportAPI.getClusters({ n_clusters: 5 }),
    enabled: false, // 禁用自动查询，改为手动触发
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">分析报告</h1>
        <p className="text-gray-600 mt-2">新闻聚类与关键词统计</p>
      </div>

      {/* Tab 切换 */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab("keywords")}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === "keywords"
                  ? "border-primary-600 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <Hash className="inline mr-2" size={18} />
              关键词 Top10
            </button>
            <button
              onClick={() => setActiveTab("clusters")}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === "clusters"
                  ? "border-primary-600 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <TrendingUp className="inline mr-2" size={18} />
              聚类分析
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === "keywords" && (
            <div className="space-y-6">
              {/* 时间范围选择 */}
              <div className="flex items-end gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    时间范围
                  </label>
                  <select
                    value={timeRange}
                    onChange={(e) => setTimeRange(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="daily">今日</option>
                    <option value="weekly">本周</option>
                    <option value="monthly">本月</option>
                  </select>
                </div>
                <button
                  onClick={() => refetchKeywords()}
                  disabled={loadingKeywords}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
                >
                  {loadingKeywords ? "查询中..." : "查询"}
                </button>
              </div>

              {loadingKeywords ? (
                <div className="flex justify-center py-12">
                  <LoadingSpinner text="加载中..." />
                </div>
              ) : keywordsData?.data?.keywords?.length ? (
                <div>
                  <div className="mb-4">
                    <p className="text-sm text-gray-600">
                      统计时间：{keywordsData.data.start_date} 至{" "}
                      {keywordsData.data.end_date}
                    </p>
                    <p className="text-sm text-gray-600">
                      总文章数：{keywordsData.data.total_articles}
                    </p>
                  </div>

                  {/* 图表 */}
                  <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={keywordsData.data.keywords}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="word" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#0ea5e9" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* 列表 */}
                  <div className="mt-6">
                    <h3 className="font-medium text-gray-900 mb-3">
                      关键词列表
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                      {keywordsData.data.keywords.map((kw, index) => (
                        <div
                          key={index}
                          className="p-3 bg-gray-50 rounded-lg text-center"
                        >
                          <p className="font-medium text-gray-900">{kw.word}</p>
                          <p className="text-sm text-gray-600 mt-1">
                            {kw.count} 次
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <EmptyState
                  title="暂无数据"
                  description="该时间范围内没有关键词统计"
                />
              )}
            </div>
          )}

          {activeTab === "clusters" && (
            <div className="space-y-6">
              {/* 查询按钮 */}
              <div>
                <button
                  onClick={() => refetchClusters()}
                  disabled={loadingClusters}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
                >
                  {loadingClusters ? "分析中..." : "开始分析"}
                </button>
                <p className="text-sm text-gray-500 mt-2">
                  分析最近 7 天的新闻，需要至少 10 篇文章
                </p>
              </div>

              {loadingClusters ? (
                <div className="flex justify-center py-12">
                  <LoadingSpinner text="分析中..." />
                </div>
              ) : clustersData?.data?.clusters?.length ? (
                <div>
                  <div className="mb-4">
                    <p className="text-sm text-gray-600">
                      总文章数：{clustersData.data.total_news}
                    </p>
                    <p className="text-sm text-gray-600">
                      聚类数：{clustersData.data.n_clusters}
                    </p>
                  </div>

                  {/* 聚类列表 */}
                  <div className="space-y-4">
                    {clustersData.data.clusters.map((cluster) => (
                      <div
                        key={cluster.cluster_id}
                        className="p-4 border border-gray-200 rounded-lg"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="font-medium text-gray-900">
                            聚类 {cluster.cluster_id}
                          </h3>
                          <span className="text-sm text-gray-600">
                            {cluster.size} 篇文章
                          </span>
                        </div>

                        <div className="mb-3">
                          <p className="text-sm text-gray-600 mb-2">关键词：</p>
                          <div className="flex flex-wrap gap-2">
                            {cluster.keywords.map((kw, i) => (
                              <span
                                key={i}
                                className="px-2 py-1 bg-primary-50 text-primary-700 text-xs rounded-full"
                              >
                                {kw}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div>
                          <p className="text-sm text-gray-600 mb-2">
                            示例标题：
                          </p>
                          <ul className="space-y-1">
                            {cluster.sample_titles
                              .slice(0, 3)
                              .map((title, i) => (
                                <li
                                  key={i}
                                  className="text-sm text-gray-700 truncate"
                                >
                                  • {title}
                                </li>
                              ))}
                          </ul>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <EmptyState
                  title="暂无数据"
                  description="没有足够的数据进行聚类分析"
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
