import { useState } from "react";
import {
  Upload,
  FileJson,
  FileText,
  FileSpreadsheet,
  CheckCircle,
  AlertCircle,
  Loader2,
  Trash2,
  Plus,
} from "lucide-react";
import { Header } from "../components/Layout/Header";

export default function Ingest() {
  const [uploadedFiles, setUploadedFiles] = useState([
    {
      id: 1,
      name: "news_data.json",
      type: "json",
      size: "2.5 MB",
      status: "completed",
      progress: 100,
    },
    {
      id: 2,
      name: "tech_news.txt",
      type: "text",
      size: "1.2 MB",
      status: "completed",
      progress: 100,
    },
    {
      id: 3,
      name: "news_batch.xlsx",
      type: "excel",
      size: "5.8 MB",
      status: "processing",
      progress: 65,
    },
  ]);
  const [dataType, setDataType] = useState("structured");
  const [jsonContent, setJsonContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fileTypes = [
    { id: "json", label: "JSON 文件", icon: FileJson, color: "bg-blue-500" },
    { id: "text", label: "纯文本/HTML", icon: FileText, color: "bg-green-500" },
    {
      id: "excel",
      label: "Excel 文件",
      icon: FileSpreadsheet,
      color: "bg-orange-500",
    },
  ];

  const handleSubmit = async () => {
    if (!jsonContent.trim()) return;
    setIsSubmitting(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsSubmitting(false);
    alert("数据入库成功！");
    setJsonContent("");
  };

  const handleFileUpload = (type: string) => {
    const newFile = {
      id: Date.now(),
      name: `upload_${Date.now()}.${type}`,
      type,
      size: `${(Math.random() * 5 + 0.5).toFixed(1)} MB`,
      status: "processing" as const,
      progress: 0,
    };
    setUploadedFiles((prev) => [newFile, ...prev]);

    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 20;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
      }
      setUploadedFiles((prev) =>
        prev.map((f) =>
          f.id === newFile.id
            ? {
                ...f,
                progress,
                status:
                  progress === 100
                    ? ("completed" as const)
                    : ("processing" as const),
              }
            : f,
        ),
      );
    }, 300);
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header title="数据入库" subtitle="上传新闻数据到知识库" />

      <main className="flex-1 p-6 overflow-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <div className="card-header">
              <h3 className="font-semibold text-gray-800">数据类型选择</h3>
            </div>
            <div className="card-body">
              <div className="flex items-center gap-4 mb-6">
                <button
                  onClick={() => setDataType("structured")}
                  className={`flex-1 py-3 px-4 rounded-xl border-2 transition-all ${
                    dataType === "structured"
                      ? "border-primary-500 bg-primary-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <span
                    className={`font-medium ${dataType === "structured" ? "text-primary-600" : "text-gray-600"}`}
                  >
                    结构化数据
                  </span>
                </button>
                <button
                  onClick={() => setDataType("unstructured")}
                  className={`flex-1 py-3 px-4 rounded-xl border-2 transition-all ${
                    dataType === "unstructured"
                      ? "border-primary-500 bg-primary-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <span
                    className={`font-medium ${dataType === "unstructured" ? "text-primary-600" : "text-gray-600"}`}
                  >
                    非结构化数据
                  </span>
                </button>
              </div>

              {dataType === "structured" ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    JSON 数据输入
                  </label>
                  <textarea
                    value={jsonContent}
                    onChange={(e) => setJsonContent(e.target.value)}
                    placeholder='[{"title": "新闻标题", "content": "新闻内容", "source": "来源", "publish_date": "2026-07-11", "category": "科技"}]'
                    className="input-field resize-none h-48 font-mono text-sm"
                  />
                  <button
                    onClick={handleSubmit}
                    disabled={isSubmitting || !jsonContent.trim()}
                    className="mt-4 btn-primary w-full flex items-center justify-center gap-2"
                  >
                    {isSubmitting ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Upload className="w-5 h-5" />
                    )}
                    {isSubmitting ? "入库中..." : "提交入库"}
                  </button>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    文本/HTML 内容输入
                  </label>
                  <textarea
                    placeholder="粘贴新闻正文内容或HTML代码..."
                    className="input-field resize-none h-48 font-mono text-sm"
                  />
                  <button className="mt-4 btn-primary w-full flex items-center justify-center gap-2">
                    <Upload className="w-5 h-5" />
                    提交入库
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header flex items-center justify-between">
              <h3 className="font-semibold text-gray-800">文件上传</h3>
              <button className="text-sm text-primary-500 hover:text-primary-600">
                清空列表
              </button>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-3 gap-3 mb-4">
                {fileTypes.map((fileType) => {
                  const Icon = fileType.icon;
                  return (
                    <button
                      key={fileType.id}
                      onClick={() => handleFileUpload(fileType.id)}
                      className="flex flex-col items-center gap-3 p-4 border-2 border-dashed border-gray-300 rounded-xl hover:border-primary-500 hover:bg-primary-50 transition-all"
                    >
                      <div
                        className={`w-12 h-12 ${fileType.color} rounded-xl flex items-center justify-center`}
                      >
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <span className="text-sm font-medium text-gray-700">
                        {fileType.label}
                      </span>
                    </button>
                  );
                })}
              </div>

              <div className="space-y-3">
                {uploadedFiles.map((file) => (
                  <div
                    key={file.id}
                    className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl"
                  >
                    <div
                      className={`w-10 h-10 ${file.type === "json" ? "bg-blue-100" : file.type === "text" ? "bg-green-100" : "bg-orange-100"} rounded-lg flex items-center justify-center`}
                    >
                      {file.type === "json" && (
                        <FileJson className="w-5 h-5 text-blue-600" />
                      )}
                      {file.type === "text" && (
                        <FileText className="w-5 h-5 text-green-600" />
                      )}
                      {file.type === "excel" && (
                        <FileSpreadsheet className="w-5 h-5 text-orange-600" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-800">
                        {file.name}
                      </p>
                      <div className="mt-1 w-full bg-gray-200 rounded-full h-1.5">
                        <div
                          className={`h-1.5 rounded-full ${file.status === "completed" ? "bg-green-500" : "bg-primary-500"}`}
                          style={{ width: `${file.progress}%` }}
                        ></div>
                      </div>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-xs text-gray-500">
                          {file.size}
                        </span>
                        <span
                          className={`text-xs ${file.status === "completed" ? "text-green-500" : "text-primary-500"}`}
                        >
                          {file.status === "completed"
                            ? "已完成"
                            : `${file.progress}%`}
                        </span>
                      </div>
                    </div>
                    <button className="p-2 hover:bg-gray-200 rounded-lg transition-colors">
                      <Trash2 className="w-4 h-4 text-gray-400" />
                    </button>
                  </div>
                ))}
              </div>

              {uploadedFiles.length > 0 && (
                <button className="mt-4 btn-primary w-full flex items-center justify-center gap-2">
                  <Plus className="w-5 h-5" />
                  添加更多文件
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="mt-6 card">
          <div className="card-header">
            <h3 className="font-semibold text-gray-800">入库统计</h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-800">1,247</p>
                  <p className="text-sm text-gray-500">成功入库</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-yellow-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-800">32</p>
                  <p className="text-sm text-gray-500">重复跳过</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-800">8</p>
                  <p className="text-sm text-gray-500">入库失败</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                  <Loader2 className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-800">5</p>
                  <p className="text-sm text-gray-500">处理中</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
