"""
检索 Skill：封装 FAISS 检索和重排序功能
"""
from typing import List, Dict, Any, Optional
from loguru import logger

from core.embeddings import get_embedding_model
from core.reranker import get_reranker
from core.vectorstore import get_vector_store
from db.dao import ChunkDAO, ArticleDAO
from db.models import SessionLocal
from config import settings
from .base_skill import BaseSkill


class RetrievalSkill(BaseSkill):
    """检索 Skill：封装 FAISS 检索和重排序功能"""
    
    def __init__(self):
        super().__init__()
        self.embedding_model = get_embedding_model()
        self.reranker = get_reranker()
        self.vector_store = get_vector_store()
        self.retrieval_top_k = settings.RAG_RETRIEVAL_TOP_K
        self.rerank_top_k = settings.RAG_RERANK_TOP_K
        self.similarity_threshold = settings.RAG_SIMILARITY_THRESHOLD
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        语义检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            threshold: 相似度阈值
        
        Returns:
            检索结果列表
        """
        threshold = threshold or self.similarity_threshold
        top_k = top_k or self.rerank_top_k
        
        logger.info(f"检索 Skill 执行搜索: '{query[:50]}...', top_k={top_k}")
        
        # 向量化查询
        query_vector = self.embedding_model.encode_query(query)
        
        # FAISS 召回
        embedding_ids, distances = self.vector_store.search(
            query_vector,
            top_k=self.retrieval_top_k
        )
        
        if not embedding_ids:
            logger.warning("FAISS 召回为空")
            return {"sources": [], "retrieval_stats": {"total_retrieved": 0}}
        
        # 转换距离为相似度
        similarities = [
            self.vector_store.distance_to_similarity(dist)
            for dist in distances
        ]
        
        logger.debug(f"召回 {len(embedding_ids)} 个结果，最高相似度: {max(similarities):.4f}")
        
        # 获取文本与元数据
        db = SessionLocal()
        try:
            chunks = ChunkDAO.get_by_embedding_ids(db, embedding_ids)
            
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
        
        # 重排序
        if len(candidates) > 1:
            logger.debug(f"重排序 Top-{top_k}")
            reranked = self.reranker.rerank_with_data(
                query=query,
                data_list=candidates,
                text_key='text',
                top_k=top_k
            )
            final_candidates = reranked
        else:
            final_candidates = candidates[:top_k]
        
        # 过滤低相似度结果
        final_candidates = [
            c for c in final_candidates
            if c.get('retrieval_score', 0) >= threshold
        ]
        
        return {
            "sources": final_candidates,
            "retrieval_stats": {
                "total_retrieved": len(embedding_ids),
                "total_reranked": len(final_candidates),
                "avg_retrieval_score": sum(similarities) / len(similarities) if similarities else 0,
                "method": "faiss_rerank"
            }
        }
    
    def rerank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """
        结果重排序
        
        Args:
            query: 查询文本
            candidates: 候选结果列表
        
        Returns:
            重排序结果
        """
        if not candidates:
            return []
        
        logger.debug(f"重排序 {len(candidates)} 个候选结果")
        
        return self.reranker.rerank_with_data(
            query=query,
            data_list=candidates,
            text_key='text',
            top_k=self.rerank_top_k
        )
    
    def hybrid_search(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        混合检索（向量+关键词）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
        
        Returns:
            混合结果
        """
        top_k = top_k or self.rerank_top_k
        
        logger.info(f"混合检索: '{query[:50]}...'")
        
        vector_result = self.search(query, top_k=top_k)
        
        return {
            "sources": vector_result["sources"],
            "retrieval_stats": {
                **vector_result["retrieval_stats"],
                "method": "hybrid"
            }
        }
    
    def execute(self, **kwargs) -> Any:
        """执行技能"""
        action = kwargs.get('action', 'search')
        
        if action == 'search':
            return self.search(
                query=kwargs['query'],
                top_k=kwargs.get('top_k'),
                threshold=kwargs.get('threshold')
            )
        elif action == 'rerank':
            return self.rerank(
                query=kwargs['query'],
                candidates=kwargs['candidates']
            )
        elif action == 'hybrid_search':
            return self.hybrid_search(
                query=kwargs['query'],
                top_k=kwargs.get('top_k')
            )
        
        return {"error": f"不支持的操作: {action}"}
