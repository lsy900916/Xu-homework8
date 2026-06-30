"""
Embedding 模块单元测试
"""
import pytest
import numpy as np
from core.embeddings import EmbeddingModel


class TestEmbeddingModel:
    """测试 Embedding 模型"""
    
    @pytest.fixture
    def embedding_model(self):
        """Fixture: Embedding 模型实例"""
        return EmbeddingModel()
    
    def test_encode_single_text(self, embedding_model):
        """测试单个文本向量化"""
        text = "这是一个测试文本"
        vector = embedding_model.encode_query(text)
        
        assert vector is not None
        assert isinstance(vector, np.ndarray)
        assert vector.shape == (embedding_model.dimension,)
        assert vector.dtype == np.float32
    
    def test_encode_batch(self, embedding_model):
        """测试批量文本向量化"""
        texts = [
            "第一个测试文本",
            "第二个测试文本",
            "第三个测试文本"
        ]
        
        vectors = embedding_model.encode_batch(texts)
        
        assert vectors is not None
        assert isinstance(vectors, np.ndarray)
        assert vectors.shape == (len(texts), embedding_model.dimension)
        assert vectors.dtype == np.float32
    
    def test_encode_empty_list(self, embedding_model):
        """测试空列表向量化"""
        vectors = embedding_model.encode([])
        
        assert vectors is not None
        assert len(vectors) == 0
    
    def test_similarity(self, embedding_model):
        """测试相似度计算"""
        text1 = "人工智能技术发展迅速"
        text2 = "AI 技术进步很快"
        text3 = "今天天气很好"
        
        vec1 = embedding_model.encode_query(text1)
        vec2 = embedding_model.encode_query(text2)
        vec3 = embedding_model.encode_query(text3)
        
        sim_12 = embedding_model.similarity(vec1, vec2)
        sim_13 = embedding_model.similarity(vec1, vec3)
        
        # 相似文本的相似度应该更高
        assert sim_12 > sim_13
        assert 0 <= sim_12 <= 1
        assert 0 <= sim_13 <= 1

