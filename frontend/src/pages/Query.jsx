/**
 * RAG 查询页面
 */
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { ragAPI } from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";
import { Send, ExternalLink, AlertCircle, MessageSquare } from "lucide-react";
import toast from "react-hot-toast";

export default function Query() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);

  const queryMutation = useMutation({
    mutationFn: ragAPI.query,
    onSuccess: (response) => {
      setResult(response.data);
      toast.success("查询成功！");
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!question.trim()) {
      toast.error("请输入问题");
      return;
    }

    queryMutation.mutate({
      question: question.trim(),
      top_k: 5,
      enable_rerank: true,
      enable_fallback: true,
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">知识库查询</h1>
        <p className="text-gray-600 mt-2">基于 RAG 的智能问答系统</p>
      </div>

      {/* 查询表单 */}
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              您的问题
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              rows={4}
              placeholder="例如：最近关于人工智能的新闻有哪些？"
            />
          </div>

          <button
            type="submit"
            disabled={queryMutation.isPending}
            className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {queryMutation.isPending ? (
              <>
                <LoadingSpinner size="sm" />
                <span>查询中...</span>
              </>
            ) : (
              <>
                <Send size={20} />
                <span>提问</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* 查询结果 */}
      {result && (
        <div className="space-y-6">
          {/* AI 答案 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
              <MessageSquare className="text-primary-600" size={24} />
              AI 回答
            </h2>
            <div className="prose max-w-none">
              <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                {result.answer}
              </p>
            </div>

            {/* 回退搜索提示 */}
            {result.fallback_used && (
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-2">
                <AlertCircle
                  className="text-yellow-600 flex-shrink-0 mt-0.5"
                  size={18}
                />
                <p className="text-sm text-yellow-800">
                  本地检索结果不足，已使用网络搜索补充
                </p>
              </div>
            )}

            {/* 统计信息 */}
            <div className="mt-4 pt-4 border-t flex flex-wrap gap-4 text-sm text-gray-600">
              <span>检索方法: {result.retrieval_stats.method}</span>
              <span>召回数量: {result.retrieval_stats.total_retrieved}</span>
              <span>重排后: {result.retrieval_stats.total_reranked}</span>
              <span>
                LLM 耗时: {result.llm_stats.response_time.toFixed(2)}s
              </span>
              <span>总耗时: {result.total_time.toFixed(2)}s</span>
            </div>
          </div>

          {/* 引用来源 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">引用来源</h2>
            <div className="space-y-4">
              {result.sources.map((source, index) => (
                <div
                  key={index}
                  className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-1 rounded">
                          来源 {index + 1}
                        </span>
                        {source.source_type === "fallback" && (
                          <span className="text-xs font-medium text-yellow-600 bg-yellow-50 px-2 py-1 rounded">
                            网络搜索
                          </span>
                        )}
                      </div>
                      <h3 className="font-medium text-gray-900 mb-2">
                        {source.article_title || "无标题"}
                      </h3>
                      <p className="text-sm text-gray-600 line-clamp-3">
                        {source.text}
                      </p>
                      {source.article_url && (
                        <a
                          href={source.article_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 mt-2"
                        >
                          查看原文
                          <ExternalLink size={14} />
                        </a>
                      )}
                    </div>
                    <div className="text-right">
                      {source.retrieval_score !== undefined && (
                        <p className="text-xs text-gray-500">
                          相似度: {source.retrieval_score.toFixed(3)}
                        </p>
                      )}
                      {source.rerank_score !== undefined && (
                        <p className="text-xs text-gray-500">
                          重排分数: {source.rerank_score.toFixed(3)}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
