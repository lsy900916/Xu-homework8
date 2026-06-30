"""
Embedding 模块：all-MiniLM-L6-v2
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from loguru import logger

from config import settings


class EmbeddingModel:
    """Embedding 模型封装"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        self.batch_size = settings.EMBEDDING_BATCH_SIZE
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        try:
            logger.info(f"加载 Embedding 模型: {self.model_name}")
            # 强制使用 CPU，避免某些环境下 device_map/accelerate 导致 meta tensor 问题
            self.model = SentenceTransformer(self.model_name, device='cpu')
            logger.info(f"Embedding 模型加载成功，维度: {self.dimension}")
        except Exception as e:
            logger.error(f"Embedding 模型加载失败: {e}")
            raise
    
    def encode(self, texts: Union[str, List[str]], batch_size: int = None) -> np.ndarray:
        """
        文本向量化
        
        Args:
            texts: 单个文本或文本列表
            batch_size: 批量大小
            
        Returns:
            numpy.ndarray: 向量数组，形状 (n, dimension)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return np.array([])
        
        batch_size = batch_size or self.batch_size
        
        try:
            logger.debug(f"开始向量化 {len(texts)} 条文本，批量大小: {batch_size}")
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True  # L2 归一化
            )
            
            logger.debug(f"向量化完成，输出形状: {embeddings.shape}")
            
            return embeddings.astype('float32')
        
        except Exception as e:
            # 针对 meta tensor 报错做一次安全重载与重试
            msg = str(e)
            logger.error(f"向量化失败: {msg}")
            if 'meta tensor' in msg.lower():
                logger.warning("检测到 meta tensor 错误，尝试以 CPU 方式重载模型并重试一次")
                try:
                    self._load_model()
                    embeddings = self.model.encode(
                        texts,
                        batch_size=batch_size,
                        show_progress_bar=False,
                        convert_to_numpy=True,
                        normalize_embeddings=True
                    )
                    logger.debug(f"向量化重试完成，输出形状: {embeddings.shape}")
                    return embeddings.astype('float32')
                except Exception as e2:
                    logger.error(f"向量化重试仍失败: {e2}")
                    raise
            raise
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        查询文本向量化（单条）
        
        Args:
            query: 查询文本
            
        Returns:
            numpy.ndarray: 向量，形状 (dimension,)
        """
        embeddings = self.encode([query])
        return embeddings[0]
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        批量文本向量化
        
        Args:
            texts: 文本列表
            
        Returns:
            numpy.ndarray: 向量数组，形状 (n, dimension)
        """
        return self.encode(texts)
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            float: 相似度 [0, 1]
        """
        # 由于已经 L2 归一化，直接点积即为余弦相似度
        return np.dot(vec1, vec2)


# 单例模式
_embedding_model = None


def get_embedding_model() -> EmbeddingModel:
    """获取 Embedding 模型单例"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model

