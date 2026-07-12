"""
搜索工具：封装百度搜索 API 调用
"""
from typing import List, Dict, Any, Optional
from loguru import logger
import requests

from services.search_fallback import search_fallback, search_baidu_real
from config import settings
from .base_tool import BaseTool


class SearchTool(BaseTool):
    """搜索工具：封装百度搜索 API 调用"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.BAIDU_API_KEY
        self.secret_key = settings.BAIDU_SECRET_KEY
    
    def search_baidu(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """
        百度搜索
        
        Args:
            query: 查询词
            num_results: 返回结果数量
        
        Returns:
            搜索结果
        """
        logger.info(f"搜索工具执行百度搜索: '{query}', num_results={num_results}")
        
        if self.api_key and self.secret_key:
            return search_baidu_real(query, self.api_key, self.secret_key, num_results)
        else:
            return search_fallback(query, num_results)
    
    def search_rss(self, rss_url: str) -> List[Dict[str, Any]]:
        """
        RSS 订阅解析
        
        Args:
            rss_url: RSS 订阅地址
        
        Returns:
            RSS 条目
        """
        logger.info(f"搜索工具执行 RSS 解析: {rss_url}")
        
        try:
            import feedparser
            
            feed = feedparser.parse(rss_url)
            
            results = []
            for entry in feed.entries[:10]:
                results.append({
                    "title": entry.title,
                    "url": entry.link,
                    "snippet": entry.summary if hasattr(entry, 'summary') else '',
                    "published": entry.published if hasattr(entry, 'published') else ''
                })
            
            logger.info(f"RSS 解析完成，获取 {len(results)} 条条目")
            
            return results
        
        except ImportError:
            logger.error("未安装 feedparser 库")
            return []
        except Exception as e:
            logger.error(f"RSS 解析失败: {e}")
            return []
    
    def search_local(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        本地知识库检索
        
        Args:
            query: 查询词
            top_k: 返回结果数量
        
        Returns:
            检索结果
        """
        logger.info(f"搜索工具执行本地检索: '{query}', top_k={top_k}")
        
        from agent.skills import RetrievalSkill
        
        retrieval_skill = RetrievalSkill()
        result = retrieval_skill.search(query, top_k=top_k)
        
        return result.get('sources', [])
    
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        action = kwargs.get('action', 'search_baidu')
        
        if action == 'search_baidu':
            return self.search_baidu(
                query=kwargs['query'],
                num_results=kwargs.get('num_results', 3)
            )
        elif action == 'search_rss':
            return self.search_rss(
                rss_url=kwargs['rss_url']
            )
        elif action == 'search_local':
            return self.search_local(
                query=kwargs['query'],
                top_k=kwargs.get('top_k', 5)
            )
        
        return {"error": f"不支持的操作: {action}"}
