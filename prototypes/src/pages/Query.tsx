import { useState, KeyboardEvent } from "react";
import {
  Send,
  Sparkles,
  MessageCircle,
  ExternalLink,
  ThumbsUp,
  ThumbsDown,
  History,
} from "lucide-react";
import { Header } from "../components/Layout/Header";

const mockSources = [
  {
    id: 1,
    title: "人工智能大模型最新进展",
    source: "科技日报",
    similarity: 0.89,
    rerank_score: 0.95,
  },
  {
    id: 2,
    title: "RAG技术在企业中的应用",
    source: "人工智能杂志",
    similarity: 0.82,
    rerank_score: 0.88,
  },
  {
    id: 3,
    title: "Qwen系列模型技术解析",
    source: "开源社区",
    similarity: 0.78,
    rerank_score: 0.85,
  },
];

const mockHistory = [
  {
    id: 1,
    query: "最近关于人工智能的新闻有哪些？",
    time: "10分钟前",
    source: "本地",
  },
  { id: 2, query: "RAG技术是什么？", time: "30分钟前", source: "本地" },
  { id: 3, query: "Ollama如何部署？", time: "1小时前", source: "网络" },
];

export default function Query() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState(mockSources);

  const handleSubmit = async () => {
    if (!query.trim()) return;

    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 2500));
    setLoading(false);

    setAnswer(`根据您的问题"${query}"，结合知识库中的新闻内容，为您整理以下信息：

人工智能技术近年来发展迅速，特别是大语言模型领域。最新发布的Qwen 2.5系列模型在性能和效率上都有显著提升，支持更长的上下文窗口和更精准的语义理解。

RAG（检索增强生成）技术通过将向量检索与大语言模型相结合，能够提供更加准确和可溯源的回答。该技术在企业知识库建设、智能问答系统等领域得到广泛应用。

建议您关注科技日报、人工智能杂志等权威来源，获取最新的行业动态和技术进展。`);
  };

  const handleKeyPress = (e: KeyboardEvent) => {
    if (e.key === "Enter" && !loading) {
      handleSubmit();
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header title="智能问答" subtitle="基于RAG技术的新闻智能问答系统" />

      <main className="flex-1 p-6 overflow-auto">
        <div className="max-w-4xl mx-auto">
          <div className="card">
            <div className="card-body">
              <div className="relative">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="请输入您的问题，例如：最近关于人工智能的新闻有哪些？"
                  className="w-full px-6 py-4 border-2 border-gray-200 rounded-xl resize-none focus:border-primary-500 focus:ring-4 focus:ring-primary-100 transition-all duration-200 outline-none text-gray-800"
                  rows={3}
                  disabled={loading}
                />
                <button
                  onClick={handleSubmit}
                  disabled={loading || !query.trim()}
                  className="absolute right-3 bottom-3 btn-primary flex items-center gap-2 px-6"
                >
                  {loading ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                  {loading ? "思考中..." : "提问"}
                </button>
              </div>

              {!loading && !answer && (
                <div className="mt-4 flex items-center gap-2 text-sm text-gray-500">
                  <Sparkles className="w-4 h-4 text-primary-500" />
                  <span>
                    支持自然语言提问，系统将基于知识库内容生成准确答案
                  </span>
                </div>
              )}
            </div>
          </div>

          {answer && (
            <div className="mt-6 card animate-fadeIn">
              <div className="card-header flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <MessageCircle className="w-5 h-5 text-primary-500" />
                  <h3 className="font-semibold text-gray-800">回答结果</h3>
                </div>
                <div className="flex items-center gap-2">
                  <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                    <ThumbsUp className="w-5 h-5 text-gray-500 hover:text-green-500" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                    <ThumbsDown className="w-5 h-5 text-gray-500 hover:text-red-500" />
                  </button>
                </div>
              </div>
              <div className="card-body">
                <div className="prose prose-sm max-w-none">
                  {answer.split("\n").map((paragraph, index) => (
                    <p
                      key={index}
                      className="text-gray-700 leading-relaxed mb-4"
                    >
                      {paragraph}
                    </p>
                  ))}
                </div>
              </div>
            </div>
          )}

          {answer && (
            <div className="mt-6 card animate-fadeIn">
              <div className="card-header">
                <h3 className="font-semibold text-gray-800">来源引用</h3>
              </div>
              <div className="card-body">
                <div className="space-y-3">
                  {sources.map((source) => (
                    <div
                      key={source.id}
                      className="flex items-start gap-4 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex-shrink-0 w-2 h-full bg-primary-500 rounded-full"></div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium text-gray-800">
                            {source.title}
                          </h4>
                          <button className="text-primary-500 hover:text-primary-600">
                            <ExternalLink className="w-4 h-4" />
                          </button>
                        </div>
                        <div className="flex items-center gap-4 mt-2 text-sm">
                          <span className="text-gray-500">
                            来源: {source.source}
                          </span>
                          <span className="text-primary-600">
                            相似度: {source.similarity * 100}%
                          </span>
                          <span className="text-secondary-600">
                            重排得分: {source.rerank_score * 100}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div className="mt-6 card">
            <div className="card-header flex items-center gap-2">
              <History className="w-5 h-5 text-gray-500" />
              <h3 className="font-semibold text-gray-800">历史记录</h3>
            </div>
            <div className="card-body">
              <div className="space-y-2">
                {mockHistory.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-800 truncate">
                        {item.query}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {item.time}
                      </p>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${item.source === "本地" ? "bg-green-100 text-green-600" : "bg-blue-100 text-blue-600"}`}
                    >
                      {item.source}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
