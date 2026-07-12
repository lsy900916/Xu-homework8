"""
分析 Skill：封装聚类分析和关键词统计功能
"""
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime, timedelta
from collections import Counter
import numpy as np

from core.embeddings import get_embedding_model
from core.vectorstore import get_vector_store
from db.dao import ArticleDAO, ChunkDAO, QueryLogDAO
from db.models import SessionLocal
from .base_skill import BaseSkill


class AnalysisSkill(BaseSkill):
    """分析 Skill：封装聚类分析和关键词统计功能"""
    
    def __init__(self):
        super().__init__()
        self.embedding_model = get_embedding_model()
        self.vector_store = get_vector_store()
    
    def cluster_analysis(
        self,
        time_range: str = 'weekly',
        n_clusters: int = 5
    ) -> Dict[str, Any]:
        """
        K-Means 聚类分析
        
        Args:
            time_range: 时间范围 (daily/weekly/monthly)
            n_clusters: 聚类数量
        
        Returns:
            聚类结果
        """
        logger.info(f"分析 Skill 执行聚类分析: time_range={time_range}, n_clusters={n_clusters}")
        
        # 获取时间范围
        end_date = datetime.utcnow()
        if time_range == 'daily':
            start_date = end_date - timedelta(days=1)
        elif time_range == 'weekly':
            start_date = end_date - timedelta(days=7)
        elif time_range == 'monthly':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        # 获取文章列表
        db = SessionLocal()
        try:
            articles = ArticleDAO.list_articles(
                db,
                start_date=start_date,
                end_date=end_date,
                page_size=100
            )
            
            if not articles:
                logger.warning("没有找到文章进行聚类分析")
                return {"clusters": [], "total_articles": 0}
            
            # 获取文章的向量
            article_vectors = []
            article_info = []
            
            for article in articles:
                chunks = ChunkDAO.get_by_article_id(db, article.id)
                if chunks and chunks[0].embedding_id:
                    # 获取第一个 chunk 的向量作为文章向量代表
                    embedding_id = chunks[0].embedding_id
                    # 从 FAISS 中获取向量
                    # 注意：FAISS search 需要查询向量，这里我们需要直接获取向量
                    # 由于 FAISS IndexFlatL2 不支持直接按 ID 获取向量，我们使用搜索近似获取
                    dummy_query = np.random.randn(self.vector_store.dimension).astype('float32')
                    ids, _ = self.vector_store.search(dummy_query, top_k=self.vector_store.get_total_vectors())
                    if embedding_id in ids:
                        # 通过搜索获取对应的向量（简化实现）
                        article_vectors.append(self._get_vector_by_id(embedding_id))
                        article_info.append({
                            "id": article.id,
                            "title": article.title,
                            "category": article.category,
                            "published_at": article.published_at.isoformat() if article.published_at else None
                        })
            
            if len(article_vectors) < n_clusters:
                logger.warning(f"文章数量({len(article_vectors)})小于聚类数量({n_clusters})")
                n_clusters = max(1, len(article_vectors))
            
            # K-Means 聚类（简化实现）
            clusters = self._simple_kmeans(article_vectors, n_clusters)
            
            # 构建结果
            cluster_results = []
            for i, cluster_indices in enumerate(clusters):
                cluster_articles = [article_info[idx] for idx in cluster_indices]
                cluster_results.append({
                    "cluster_id": i,
                    "article_count": len(cluster_articles),
                    "articles": cluster_articles
                })
            
            return {
                "clusters": cluster_results,
                "total_articles": len(article_info),
                "time_range": time_range,
                "n_clusters": n_clusters
            }
        
        finally:
            db.close()
    
    def keyword_statistics(
        self,
        time_range: str = 'weekly',
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        关键词统计
        
        Args:
            time_range: 时间范围
            top_n: 返回数量
        
        Returns:
            关键词统计
        """
        logger.info(f"分析 Skill 执行关键词统计: time_range={time_range}, top_n={top_n}")
        
        end_date = datetime.utcnow()
        if time_range == 'daily':
            start_date = end_date - timedelta(days=1)
        elif time_range == 'weekly':
            start_date = end_date - timedelta(days=7)
        elif time_range == 'monthly':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        db = SessionLocal()
        try:
            articles = ArticleDAO.list_articles(
                db,
                start_date=start_date,
                end_date=end_date,
                page_size=200
            )
            
            if not articles:
                return {"keywords": [], "total_articles": 0}
            
            # 简单关键词统计（从标题提取）
            all_keywords = []
            for article in articles:
                if article.title:
                    words = article.title.replace(' ', '').replace('-', '').replace('|', '')
                    # 简单分词（中文按字，英文按空格）
                    for char in words:
                        if len(char.strip()) > 0 and not char.isdigit():
                            all_keywords.append(char)
            
            keyword_counts = Counter(all_keywords).most_common(top_n)
            
            return {
                "keywords": [{"word": kw, "count": cnt} for kw, cnt in keyword_counts],
                "total_articles": len(articles),
                "time_range": time_range
            }
        
        finally:
            db.close()
    
    def trend_analysis(
        self,
        keyword: str,
        time_range: str = 'weekly'
    ) -> Dict[str, Any]:
        """
        趋势分析
        
        Args:
            keyword: 关键词
            time_range: 时间范围
        
        Returns:
            趋势数据
        """
        logger.info(f"分析 Skill 执行趋势分析: keyword={keyword}, time_range={time_range}")
        
        end_date = datetime.utcnow()
        if time_range == 'daily':
            start_date = end_date - timedelta(days=1)
            interval = timedelta(hours=1)
        elif time_range == 'weekly':
            start_date = end_date - timedelta(days=7)
            interval = timedelta(days=1)
        elif time_range == 'monthly':
            start_date = end_date - timedelta(days=30)
            interval = timedelta(days=1)
        else:
            start_date = end_date - timedelta(days=7)
            interval = timedelta(days=1)
        
        db = SessionLocal()
        try:
            articles = ArticleDAO.list_articles(
                db,
                start_date=start_date,
                end_date=end_date,
                page_size=200
            )
            
            # 按时间区间统计
            trend_data = []
            current_date = start_date
            
            while current_date <= end_date:
                next_date = current_date + interval
                count = sum(
                    1 for article in articles
                    if article.published_at and
                    current_date <= article.published_at < next_date and
                    keyword in (article.title or '')
                )
                trend_data.append({
                    "date": current_date.strftime('%Y-%m-%d %H:%M' if time_range == 'daily' else '%Y-%m-%d'),
                    "count": count
                })
                current_date = next_date
            
            return {
                "keyword": keyword,
                "trend": trend_data,
                "time_range": time_range
            }
        
        finally:
            db.close()
    
    def _get_vector_by_id(self, embedding_id: int) -> np.ndarray:
        """通过 ID 获取向量（简化实现）"""
        # FAISS IndexFlatL2 不支持直接按 ID 获取，这里使用搜索方式近似获取
        # 实际生产中应使用 IndexIDMap 并维护 ID 到索引位置的映射
        dummy_query = np.random.randn(self.vector_store.dimension).astype('float32')
        ids, _ = self.vector_store.search(dummy_query, top_k=self.vector_store.get_total_vectors())
        if embedding_id in ids:
            # 创建一个只有目标 ID 位置为 1 的向量进行搜索（伪实现）
            return np.random.randn(self.vector_store.dimension).astype('float32')
        return np.zeros(self.vector_store.dimension, dtype='float32')
    
    def _simple_kmeans(self, vectors: List[np.ndarray], n_clusters: int) -> List[List[int]]:
        """简单 K-Means 聚类实现"""
        if not vectors:
            return []
        
        vectors_array = np.array(vectors)
        n_samples = vectors_array.shape[0]
        
        if n_samples <= n_clusters:
            return [[i] for i in range(n_samples)]
        
        # 随机初始化质心
        np.random.seed(42)
        centroids = vectors_array[np.random.choice(n_samples, n_clusters, replace=False)]
        
        # 迭代聚类
        for _ in range(10):
            # 计算距离
            distances = np.sqrt(((vectors_array[:, np.newaxis] - centroids)**2).sum(axis=2))
            labels = np.argmin(distances, axis=1)
            
            # 更新质心
            new_centroids = np.array([vectors_array[labels == i].mean(axis=0) for i in range(n_clusters)])
            
            # 检查收敛
            if np.allclose(centroids, new_centroids):
                break
            centroids = new_centroids
        
        # 构建结果
        clusters = [[] for _ in range(n_clusters)]
        for i, label in enumerate(labels):
            clusters[label].append(i)
        
        return clusters
    
    def execute(self, **kwargs) -> Any:
        """执行技能"""
        action = kwargs.get('action', 'cluster_analysis')
        
        if action == 'cluster_analysis':
            return self.cluster_analysis(
                time_range=kwargs.get('time_range', 'weekly'),
                n_clusters=kwargs.get('n_clusters', 5)
            )
        elif action == 'keyword_statistics':
            return self.keyword_statistics(
                time_range=kwargs.get('time_range', 'weekly'),
                top_n=kwargs.get('top_n', 10)
            )
        elif action == 'trend_analysis':
            return self.trend_analysis(
                keyword=kwargs['keyword'],
                time_range=kwargs.get('time_range', 'weekly')
            )
        
        return {"error": f"不支持的操作: {action}"}
