/**
 * 数据入库页面
 */
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { ingestAPI } from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";
import { Upload, FileText, CheckCircle, XCircle } from "lucide-react";
import toast from "react-hot-toast";

export default function Ingest() {
  const [activeTab, setActiveTab] = useState("json");
  const [jsonData, setJsonData] = useState("");
  const [textData, setTextData] = useState("");
  const [url, setUrl] = useState("");
  const [source, setSource] = useState("");
  const [result, setResult] = useState(null);

  const ingestStructuredMutation = useMutation({
    mutationFn: ingestAPI.ingestStructured,
    onSuccess: (response) => {
      setResult(response.data);
      toast.success(
        `入库完成！成功 ${response.data.success} 条，失败 ${response.data.failed} 条`,
      );
    },
  });

  const ingestUnstructuredMutation = useMutation({
    mutationFn: ingestAPI.ingestUnstructured,
    onSuccess: () => {
      toast.success("入库成功！");
      setTextData("");
      setUrl("");
    },
  });

  const handleStructuredSubmit = () => {
    try {
      const data = JSON.parse(jsonData);
      if (!Array.isArray(data)) {
        toast.error("JSON 格式错误：应为数组");
        return;
      }
      ingestStructuredMutation.mutate({ data });
    } catch (error) {
      toast.error("JSON 格式错误");
    }
  };

  const handleUnstructuredSubmit = () => {
    if (!textData || !url) {
      toast.error("请填写文本内容和 URL");
      return;
    }

    ingestUnstructuredMutation.mutate({
      content: textData,
      url,
      type: "text",
      source,
    });
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">数据入库</h1>
        <p className="text-gray-600 mt-2">上传新闻数据到知识库</p>
      </div>

      {/* Tab 切换 */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab("json")}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === "json"
                  ? "border-primary-600 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              结构化数据（JSON）
            </button>
            <button
              onClick={() => setActiveTab("text")}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === "text"
                  ? "border-primary-600 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              非结构化数据（文本）
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === "json" ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  JSON 数据（数组格式）
                </label>
                <textarea
                  value={jsonData}
                  onChange={(e) => setJsonData(e.target.value)}
                  className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
                  placeholder={`[\n  {\n    "title": "新闻标题",\n    "content": "新闻内容...",\n    "url": "https://example.com/news/1",\n    "source": "新闻来源",\n    "category": "科技"\n  }\n]`}
                />
              </div>

              <button
                onClick={handleStructuredSubmit}
                disabled={ingestStructuredMutation.isPending}
                className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
              >
                {ingestStructuredMutation.isPending ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>入库中...</span>
                  </>
                ) : (
                  <>
                    <Upload size={20} />
                    <span>开始入库</span>
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  文本内容
                </label>
                <textarea
                  value={textData}
                  onChange={(e) => setTextData(e.target.value)}
                  className="w-full h-48 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="粘贴新闻文本或 HTML 内容..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    URL *
                  </label>
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="https://example.com/news/1"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    来源（可选）
                  </label>
                  <input
                    type="text"
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="新闻来源"
                  />
                </div>
              </div>

              <button
                onClick={handleUnstructuredSubmit}
                disabled={ingestUnstructuredMutation.isPending}
                className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
              >
                {ingestUnstructuredMutation.isPending ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>入库中...</span>
                  </>
                ) : (
                  <>
                    <FileText size={20} />
                    <span>提交</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* 入库结果 */}
      {result && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">入库结果</h2>

          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{result.total}</p>
              <p className="text-sm text-gray-600 mt-1">总计</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">
                {result.success}
              </p>
              <p className="text-sm text-gray-600 mt-1">成功</p>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <p className="text-2xl font-bold text-red-600">{result.failed}</p>
              <p className="text-sm text-gray-600 mt-1">失败</p>
            </div>
          </div>

          {/* 详细结果 */}
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {result.details.map((detail, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg flex items-center gap-3 ${
                  detail.status === "success"
                    ? "bg-green-50 border border-green-200"
                    : "bg-red-50 border border-red-200"
                }`}
              >
                {detail.status === "success" ? (
                  <CheckCircle
                    className="text-green-600 flex-shrink-0"
                    size={20}
                  />
                ) : (
                  <XCircle className="text-red-600 flex-shrink-0" size={20} />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {detail.url}
                  </p>
                  {detail.chunks_count && (
                    <p className="text-xs text-gray-600">
                      切分为 {detail.chunks_count} 个块
                    </p>
                  )}
                  {detail.reason && (
                    <p className="text-xs text-red-600">{detail.reason}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
