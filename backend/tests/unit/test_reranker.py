"""
Reranker 模块单元测试
"""
import pytest
from core.reranker import Reranker


class TestReranker:
    """测试 Reranker"""
    
    @pytest.fixture
    def reranker(self):
        """Fixture: Reranker 实例"""
        return Reranker()
    
    def test_rerank(self, reranker):
        """测试重排序"""
        query = "人工智能技术"
        
        texts = [
            "人工智能技术发展迅速，应用广泛",
            "今天天气很好，阳光明媚",
            "AI 是未来科技的核心",
            "昨天去公园散步了"
        ]
        
        ranked = reranker.rerank(query, texts, top_k=3)
        
        assert len(ranked) == 3
        
        # 检查结果格式
        for idx, score in ranked:
            assert isinstance(idx, int)
            assert isinstance(score, float)
            assert 0 <= idx < len(texts)
        
        # 检查排序（得分降序）
        scores = [score for _, score in ranked]
        assert scores == sorted(scores, reverse=True)
    
    def test_rerank_with_data(self, reranker):
        """测试数据重排序"""
        query = "AI 新闻"
        
        data_list = [
            {"text": "OpenAI 发布 GPT-5", "id": 1},
            {"text": "今天天气报告", "id": 2},
            {"text": "人工智能最新进展", "id": 3}
        ]
        
        ranked_data = reranker.rerank_with_data(query, data_list, top_k=2)
        
        assert len(ranked_data) == 2
        
        # 检查是否包含 rerank_score
        for item in ranked_data:
            assert 'rerank_score' in item
            assert isinstance(item['rerank_score'], float)

