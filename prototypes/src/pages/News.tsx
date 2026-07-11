import { useState } from "react";
import {
  Search,
  Filter,
  Edit,
  Trash2,
  Eye,
  Plus,
  Download,
  Upload,
  Calendar,
  Tag,
  ExternalLink,
} from "lucide-react";
import { Header } from "../components/Layout/Header";

const mockNews = [
  {
    id: 1,
    title: "人工智能大模型最新进展：Qwen 2.5发布",
    source: "科技日报",
    category: "科技",
    tags: ["AI", "大模型"],
    publish_date: "2026-07-11",
    status: "已入库",
  },
  {
    id: 2,
    title: "全球AI投资持续升温，Q2融资达50亿美元",
    source: "财经时报",
    category: "财经",
    tags: ["AI", "投资"],
    publish_date: "2026-07-11",
    status: "已入库",
  },
  {
    id: 3,
    title: "RAG技术赋能企业知识库建设",
    source: "人工智能杂志",
    category: "科技",
    tags: ["RAG", "知识库"],
    publish_date: "2026-07-10",
    status: "已入库",
  },
  {
    id: 4,
    title: "Ollama推出全新轻量级模型系列",
    source: "开源社区",
    category: "科技",
    tags: ["Ollama", "开源"],
    publish_date: "2026-07-10",
    status: "已入库",
  },
  {
    id: 5,
    title: "大数据分析助力新闻推荐系统升级",
    source: "数据周刊",
    category: "数据",
    tags: ["大数据", "推荐"],
    publish_date: "2026-07-09",
    status: "已入库",
  },
  {
    id: 6,
    title: "自然语言处理技术在金融领域的应用",
    source: "金融科技",
    category: "财经",
    tags: ["NLP", "金融"],
    publish_date: "2026-07-09",
    status: "已入库",
  },
];

export default function News() {
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const categories = ["全部", "科技", "财经", "数据", "娱乐"];

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id],
    );
  };

  const selectAll = () => {
    setSelectedIds(mockNews.map((n) => n.id));
  };

  const clearSelection = () => {
    setSelectedIds([]);
  };

  const filteredNews = mockNews.filter((news) => {
    const matchesSearch = news.title
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesCategory =
      categoryFilter === "全部" || news.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="flex-1 flex flex-col">
      <Header title="新闻管理" subtitle="管理知识库中的新闻内容" />

      <main className="flex-1 p-6 overflow-auto">
        <div className="card mb-6">
          <div className="card-body">
            <div className="flex flex-col md:flex-row md:items-center gap-4">
              <div className="relative flex-1">
                <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="搜索新闻标题..."
                  className="input-field pl-10"
                />
              </div>
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="input-field"
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-center gap-2">
                <button className="btn-outline flex items-center gap-2">
                  <Upload className="w-4 h-4" />
                  导入
                </button>
                <button className="btn-primary flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  新增
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header flex items-center justify-between">
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={
                    selectedIds.length === mockNews.length &&
                    mockNews.length > 0
                  }
                  onChange={() =>
                    selectedIds.length === mockNews.length
                      ? clearSelection()
                      : selectAll()
                  }
                  className="w-4 h-4 text-primary-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-600">全选</span>
              </label>
              <span className="text-sm text-gray-500">
                共 {filteredNews.length} 条新闻
              </span>
            </div>
            {selectedIds.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">
                  已选择 {selectedIds.length} 条
                </span>
                <button className="btn-secondary text-sm">批量删除</button>
                <button className="btn-secondary text-sm flex items-center gap-1">
                  <Download className="w-4 h-4" />
                  导出
                </button>
              </div>
            )}
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    选择
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    标题
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    来源
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    分类
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    标签
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    发布时间
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    状态
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredNews.map((news) => (
                  <tr
                    key={news.id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(news.id)}
                        onChange={() => toggleSelect(news.id)}
                        className="w-4 h-4 text-primary-500 border-gray-300 rounded"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-800 max-w-xs truncate">
                          {news.title}
                        </span>
                        <button className="text-gray-400 hover:text-primary-500">
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {news.source}
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 bg-primary-100 text-primary-600 text-xs rounded-full">
                        {news.category}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1">
                        {news.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {news.publish_date}
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 bg-green-100 text-green-600 text-xs rounded-full">
                        {news.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setShowDetailModal(true)}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                          <Eye className="w-4 h-4 text-gray-500" />
                        </button>
                        <button
                          onClick={() => setShowEditModal(true)}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                          <Edit className="w-4 h-4 text-primary-500" />
                        </button>
                        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="card-body flex items-center justify-between">
            <div className="text-sm text-gray-500">显示 1-6 条，共 6 条</div>
            <div className="flex items-center gap-2">
              <button className="px-3 py-1 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
                上一页
              </button>
              <button className="px-3 py-1 bg-primary-500 text-white rounded-lg text-sm">
                1
              </button>
              <button className="px-3 py-1 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
                下一页
              </button>
            </div>
          </div>
        </div>

        {showEditModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="card w-full max-w-lg p-6 animate-fadeIn">
              <h3 className="text-lg font-bold text-gray-800 mb-4">编辑新闻</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    标题
                  </label>
                  <input
                    type="text"
                    className="input-field"
                    defaultValue="人工智能大模型最新进展"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      来源
                    </label>
                    <input
                      type="text"
                      className="input-field"
                      defaultValue="科技日报"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      分类
                    </label>
                    <select className="input-field">
                      <option>科技</option>
                      <option>财经</option>
                      <option>数据</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    标签
                  </label>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-1 bg-primary-100 text-primary-600 text-sm rounded-full flex items-center gap-1">
                      AI <button className="hover:text-primary-800">×</button>
                    </span>
                    <span className="px-2 py-1 bg-primary-100 text-primary-600 text-sm rounded-full flex items-center gap-1">
                      大模型{" "}
                      <button className="hover:text-primary-800">×</button>
                    </span>
                    <input
                      type="text"
                      className="input-field w-32"
                      placeholder="添加标签"
                    />
                  </div>
                </div>
                <div className="flex items-center justify-end gap-2">
                  <button
                    onClick={() => setShowEditModal(false)}
                    className="btn-secondary"
                  >
                    取消
                  </button>
                  <button className="btn-primary">保存</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {showDetailModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="card w-full max-w-2xl p-6 animate-fadeIn max-h-[80vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-800">新闻详情</h3>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
              <div className="space-y-4">
                <h2 className="text-xl font-bold text-gray-800">
                  人工智能大模型最新进展：Qwen 2.5发布
                </h2>
                <div className="flex items-center gap-4 text-sm">
                  <span className="flex items-center gap-1 text-gray-500">
                    <Tag className="w-4 h-4" /> 科技日报
                  </span>
                  <span className="px-2 py-1 bg-primary-100 text-primary-600 text-xs rounded-full">
                    科技
                  </span>
                  <span className="text-gray-500">2026-07-11</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {["AI", "大模型", "Qwen"].map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="prose prose-sm max-w-none text-gray-700">
                  <p>
                    近日，Qwen团队正式发布了Qwen 2.5系列大语言模型，这是继Qwen
                    2.0之后的又一次重大升级。新版本在性能、效率和功能上都有显著提升。
                  </p>
                  <p>
                    Qwen 2.5支持更长的上下文窗口，最高可达128K
                    tokens，能够处理更复杂的文档理解任务。同时，模型在推理速度上也有大幅提升，相同硬件条件下速度提升约30%。
                  </p>
                  <p>
                    此外，Qwen
                    2.5还引入了多项新技术，包括改进的注意力机制、更好的多语言支持等，使其在中文理解和生成任务上表现更加出色。
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
