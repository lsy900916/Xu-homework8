"""
Reranker 模块：ms-marco-MiniLM-L-6-v2
"""
from sentence_transformers import CrossEncoder
from typing import List, Tuple
from loguru import logger

from config import settings


class Reranker:
    """重排序模型封装"""
    
    def __init__(self):
        self.model_name = settings.RERANKER_MODEL
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        try:
            logger.info(f"加载 Reranker 模型: {self.model_name}")
            # 强制使用 CPU，避免加速器/设备映射导致 meta tensor 问题
            self.model = CrossEncoder(self.model_name, device='cpu')
            logger.info("Reranker 模型加载成功")
        except Exception as e:
            logger.error(f"Reranker 模型加载失败: {e}")
            raise
    
    def rerank(
        self, 
        query: str, 
        texts: List[str], 
        top_k: int = None
    ) -> List[Tuple[int, float]]:
        """
        对文本列表进行重排序
        
        Args:
            query: 查询文本
            texts: 待排序的文本列表
            top_k: 返回前 K 个结果
            
        Returns:
            List[Tuple[int, float]]: [(原始索引, 得分), ...] 按得分降序排列
        """
        if not texts:
            return []
        
        try:
            logger.debug(f"开始重排序，查询: '{query[:50]}...', 候选数: {len(texts)}")
            
            # 构建查询-文本对
            pairs = [[query, text] for text in texts]
            
            # 预测得分
            try:
                scores = self.model.predict(pairs)
            except Exception as e:
                msg = str(e)
                logger.error(f"重排序预测失败: {msg}")
                # 遇到 meta tensor 或其他错误时，回退为保持原始顺序，得分为 0
                return [(idx, 0.0) for idx in range(len(texts))][: (top_k or len(texts))]
            
            # 按得分排序（降序）
            scored_indices = [(idx, float(score)) for idx, score in enumerate(scores)]
            scored_indices.sort(key=lambda x: x[1], reverse=True)
            
            # 返回 Top-K
            if top_k is not None:
                scored_indices = scored_indices[:top_k]
            
            logger.debug(f"重排序完成，Top-1 得分: {scored_indices[0][1]:.4f}")
            
            return scored_indices
        
        except Exception as e:
            logger.error(f"重排序失败: {e}")
            raise
    
    def rerank_with_data(
        self, 
        query: str, 
        data_list: List[dict], 
        text_key: str = 'text',
        top_k: int = None
    ) -> List[dict]:
        """
        对包含文本的数据列表进行重排序
        
        Args:
            query: 查询文本
            data_list: 数据列表，每个元素是字典
            text_key: 文本字段的键名
            top_k: 返回前 K 个结果
            
        Returns:
            List[dict]: 重排后的数据列表（包含 'rerank_score' 字段）
        """
        if not data_list:
            return []
        
        # 提取文本
        texts = [item[text_key] for item in data_list]
        
        # 重排序
        ranked = self.rerank(query, texts, top_k=top_k)
        
        # 构建结果
        result = []
        for idx, score in ranked:
            item = data_list[idx].copy()
            item['rerank_score'] = score
            result.append(item)
        
        return result


# 单例模式
_reranker = None


def get_reranker() -> Reranker:
    """获取 Reranker 单例"""
    global _reranker
    if _reranker is None:
        _reranker = Reranker()
    return _reranker

