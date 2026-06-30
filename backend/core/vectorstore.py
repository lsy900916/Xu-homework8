"""
FAISS 向量存储管理
"""
import faiss
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path
import pickle
from loguru import logger

from config import settings


class FAISSVectorStore:
    """FAISS 向量存储封装"""
    
    def __init__(self):
        self.dimension = settings.EMBEDDING_DIMENSION
        self.index_path = settings.FAISS_INDEX_PATH / "index.faiss"
        self.metadata_path = settings.FAISS_INDEX_PATH / "metadata.pkl"
        self.index = None
        self.metadata = {}  # {embedding_id: {"chunk_id": ..., "article_id": ...}}
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """加载或创建索引"""
        if self.index_path.exists():
            logger.info(f"加载 FAISS 索引: {self.index_path}")
            self.index = faiss.read_index(str(self.index_path))
            
            if self.metadata_path.exists():
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
            
            logger.info(f"FAISS 索引加载成功，向量数: {self.index.ntotal}")
        else:
            logger.info("创建新的 FAISS 索引")
            # 使用 IndexFlatL2（精确搜索，适合中小规模）
            # 如果数据量大（> 10万），可改用 IndexIVFFlat
            self.index = faiss.IndexFlatL2(self.dimension)
            self.save()
            logger.info("FAISS 索引创建成功")
    
    def add(
        self, 
        vectors: np.ndarray, 
        ids: List[int],
        metadata: Optional[List[dict]] = None
    ):
        """
        添加向量到索引
        
        Args:
            vectors: 向量数组，形状 (n, dimension)
            ids: 向量 ID 列表（对应 Chunk.embedding_id）
            metadata: 元数据列表（可选）
        """
        if vectors.shape[0] != len(ids):
            raise ValueError("向量数量与 ID 数量不匹配")
        
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"向量维度错误，期望 {self.dimension}，实际 {vectors.shape[1]}")
        
        try:
            # FAISS 需要 int64 类型的 ID
            ids_array = np.array(ids, dtype='int64')
            
            # 使用 IndexIDMap 包装，支持自定义 ID
            if not isinstance(self.index, faiss.IndexIDMap):
                self.index = faiss.IndexIDMap(self.index)
            
            # 添加向量
            self.index.add_with_ids(vectors, ids_array)
            
            # 保存元数据
            if metadata:
                for i, id_ in enumerate(ids):
                    self.metadata[id_] = metadata[i]
            
            logger.info(f"成功添加 {len(ids)} 个向量到索引，当前总数: {self.index.ntotal}")
            
            # 自动保存
            self.save()
        
        except Exception as e:
            logger.error(f"添加向量失败: {e}")
            raise
    
    def search(
        self, 
        query_vector: np.ndarray, 
        top_k: int = 10
    ) -> Tuple[List[int], List[float]]:
        """
        搜索最相似的向量
        
        Args:
            query_vector: 查询向量，形状 (dimension,) 或 (1, dimension)
            top_k: 返回前 K 个结果
            
        Returns:
            (ids, distances): ID 列表和距离列表
        """
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        if self.index.ntotal == 0:
            logger.warning("索引为空，无法搜索")
            return [], []
        
        try:
            # 搜索
            distances, indices = self.index.search(
                query_vector.astype('float32'), 
                min(top_k, self.index.ntotal)
            )
            
            # 转换为列表
            ids = indices[0].tolist()
            dists = distances[0].tolist()
            
            # 过滤无效结果（-1 表示未找到）
            valid_results = [(id_, dist) for id_, dist in zip(ids, dists) if id_ != -1]
            
            if valid_results:
                ids, dists = zip(*valid_results)
                ids = list(ids)
                dists = list(dists)
            else:
                ids, dists = [], []
            
            logger.debug(f"搜索完成，返回 {len(ids)} 个结果")
            
            return ids, dists
        
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise
    
    def remove(self, ids: List[int]):
        """
        从索引中删除向量
        
        注意：IndexFlatL2 不支持删除，需要重建索引
        如需支持删除，应使用 IndexIDMap 包装
        """
        logger.warning("IndexFlatL2 不支持删除操作，如需删除请重建索引")
        # TODO: 实现重建索引逻辑
    
    def save(self):
        """保存索引到磁盘"""
        try:
            faiss.write_index(self.index, str(self.index_path))
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.debug(f"FAISS 索引已保存: {self.index_path}")
        
        except Exception as e:
            logger.error(f"保存索引失败: {e}")
            raise
    
    def get_total_vectors(self) -> int:
        """获取索引中的向量总数"""
        return self.index.ntotal if self.index else 0
    
    def distance_to_similarity(self, distance: float) -> float:
        """
        将 L2 距离转换为相似度（0-1）
        
        由于使用了 L2 归一化的向量，L2 距离与余弦相似度关系：
        L2_distance = 2 * (1 - cosine_similarity)
        因此：cosine_similarity = 1 - L2_distance / 2
        """
        return max(0.0, 1.0 - distance / 2.0)


# 单例模式
_vector_store = None


def get_vector_store() -> FAISSVectorStore:
    """获取向量存储单例"""
    global _vector_store
    if _vector_store is None:
        _vector_store = FAISSVectorStore()
    return _vector_store

