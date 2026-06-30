"""
RAG 检索增强逻辑：召回 → 重排 → 拼接上下文 → 调用 LLM
"""
from typing import List, Dict, Any, Optional
from loguru import logger
import time

from core.embeddings import get_embedding_model
from core.reranker import get_reranker
from core.vectorstore import get_vector_store
from core.llm import get_llm
from db.dao import ChunkDAO, ArticleDAO
from db.models import SessionLocal
from config import settings


class RAGPipeline:
    """RAG 流程封装"""
    
    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.reranker = get_reranker()
        self.vector_store = get_vector_store()
        self.llm = get_llm()
        
        self.retrieval_top_k = settings.RAG_RETRIEVAL_TOP_K
        self.rerank_top_k = settings.RAG_RERANK_TOP_K
        self.similarity_threshold = settings.RAG_SIMILARITY_THRESHOLD
    
    def query(
        self, 
        question: str,
        top_k: Optional[int] = None,
        enable_rerank: bool = True
    ) -> Dict[str, Any]:
        """
        RAG 查询流程
        
        Args:
            question: 用户问题
            top_k: 返回结果数量（可选）
            enable_rerank: 是否启用重排序
            
        Returns:
            {
                "answer": "生成的答案",
                "sources": [{"chunk_id": ..., "text": ..., "score": ...}],
                "retrieval_stats": {...},
                "llm_stats": {...}
            }
        """
        logger.info(f"开始 RAG 查询: '{question}'")
        
        start_time = time.time()
        
        # ==================== 步骤 1: 向量化问题 ====================
        logger.debug("步骤 1: 向量化问题")
        query_vector = self.embedding_model.encode_query(question)
        
        # ==================== 步骤 2: FAISS 召回 ====================
        logger.debug(f"步骤 2: FAISS 召回 Top-{self.retrieval_top_k}")
        embedding_ids, distances = self.vector_store.search(
            query_vector, 
            top_k=self.retrieval_top_k
        )
        
        if not embedding_ids:
            logger.warning("FAISS 召回为空")
            return self._empty_response()
        
        # 转换距离为相似度
        similarities = [
            self.vector_store.distance_to_similarity(dist) 
            for dist in distances
        ]
        
        logger.debug(f"召回 {len(embedding_ids)} 个结果，最高相似度: {max(similarities):.4f}")
        
        # ==================== 步骤 3: 获取文本与元数据 ====================
        logger.debug("步骤 3: 获取文本与元数据")
        db = SessionLocal()
        try:
            chunks = ChunkDAO.get_by_embedding_ids(db, embedding_ids)
            
            # 构建候选列表
            candidates = []
            for i, chunk in enumerate(chunks):
                article = ArticleDAO.get_by_id(db, chunk.article_id)
                candidates.append({
                    "chunk_id": chunk.id,
                    "embedding_id": chunk.embedding_id,
                    "text": chunk.chunk_text,
                    "article_id": article.id if article else None,
                    "article_title": article.title if article else None,
                    "article_url": article.url if article else None,
                    "retrieval_score": similarities[i]
                })
        finally:
            db.close()
        
        # ==================== 步骤 4: 重排序（可选）====================
        if enable_rerank and len(candidates) > 1:
            logger.debug(f"步骤 4: 重排序 Top-{self.rerank_top_k}")
            
            reranked = self.reranker.rerank_with_data(
                query=question,
                data_list=candidates,
                text_key='text',
                top_k=top_k or self.rerank_top_k
            )
            
            final_candidates = reranked
            logger.debug(f"重排后 Top-1 得分: {final_candidates[0]['rerank_score']:.4f}")
        else:
            final_candidates = candidates[:top_k or self.rerank_top_k]
        
        # 检查结果质量
        if not final_candidates or final_candidates[0].get('retrieval_score', 0) < self.similarity_threshold:
            logger.warning(f"检索质量不足（相似度 < {self.similarity_threshold}）")
            # 这里可以触发回退搜索
        
        # ==================== 步骤 5: 构建上下文 ====================
        logger.debug("步骤 5: 构建上下文")
        context = self._build_context(final_candidates)
        
        # ==================== 步骤 6: 调用 LLM 生成答案 ====================
        logger.debug("步骤 6: 调用 LLM 生成答案")
        prompt = self._build_prompt(question, context)
        
        try:
            llm_result = self.llm.generate(
                prompt=prompt,
                system_prompt="你是一个专业的新闻助手，基于提供的新闻内容回答用户问题。回答要准确、简洁，并引用来源。"
            )
            answer = llm_result['text']
        except Exception as e:
            # LLM 不可用或 meta tensor 等错误时的降级：给出基于检索片段的摘要
            logger.error(f"LLM 生成失败，使用降级答案: {e}")
            preview = "\n\n".join([f"- {c.get('article_title') or '未知标题'}: {c['text'][:120]}" for c in final_candidates[:5]])
            answer = (
                "当前生成模型不可用，已提供基于检索内容的要点摘要：\n" + preview
            )
            llm_result = { 'text': answer, 'response_time': 0.0, 'tokens': 0, 'model': 'fallback' }
        
        # ==================== 返回结果 ====================
        total_time = time.time() - start_time
        
        logger.info(f"RAG 查询完成，耗时: {total_time:.2f}s")
        
        # 友好化标题与文本
        def _short_title(t: Optional[str]) -> str:
            if not t:
                return '未知标题'
            t = ' '.join(str(t).split())
            return (t[:80] + '...') if len(t) > 80 else t

        def _short_text(t: str) -> str:
            if not t:
                return ''
            t = ' '.join(str(t).split())
            return (t[:200] + '...') if len(t) > 200 else t

        return {
            "answer": answer,
            "sources": [
                {
                    "chunk_id": c['chunk_id'],
                    "text": _short_text(c['text']),
                    "article_title": _short_title(c.get('article_title')),
                    "article_url": c.get('article_url'),
                    "retrieval_score": c['retrieval_score'],
                    "rerank_score": c.get('rerank_score')
                }
                for c in final_candidates
            ],
            "retrieval_stats": {
                "total_retrieved": len(embedding_ids),
                "total_reranked": len(final_candidates),
                "avg_retrieval_score": sum(similarities) / len(similarities) if similarities else 0,
                "method": "faiss_rerank" if enable_rerank else "faiss_only"
            },
            "llm_stats": {
                "model": self.llm.model,
                "response_time": llm_result['response_time'],
                "tokens": llm_result['tokens']
            },
            "total_time": total_time
        }
    
    def _build_context(self, candidates: List[Dict[str, Any]]) -> str:
        """构建上下文"""
        context_parts = []
        for i, cand in enumerate(candidates, 1):
            title = cand.get('article_title', '未知')
            text = cand['text']
            context_parts.append(f"[来源 {i}] {title}\n{text}")
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """构建 LLM Prompt"""
        return f"""请基于以下新闻内容回答用户的问题。

新闻内容：
{context}

用户问题：{question}

请提供准确、简洁的答案，并在答案中标注来源（如"根据来源1..."）。如果新闻内容无法回答问题，请明确说明。

答案："""
    
    def _empty_response(self) -> Dict[str, Any]:
        """空结果响应"""
        return {
            "answer": "抱歉，未找到相关内容。",
            "sources": [],
            "retrieval_stats": {
                "total_retrieved": 0,
                "total_reranked": 0,
                "method": "empty"
            },
            "llm_stats": {},
            "total_time": 0
        }


# 单例模式
_rag_pipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """获取 RAG Pipeline 单例"""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline

