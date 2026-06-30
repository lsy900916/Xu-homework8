"""
百度搜索 API 封装（回退搜索）
"""
from typing import List, Dict, Any, Optional
from loguru import logger
import requests
from config import settings


def search_fallback(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    调用百度搜索 API
    
    Args:
        query: 查询词
        top_k: 返回结果数量
        
    Returns:
        [
            {
                "title": "搜索结果标题",
                "url": "https://...",
                "snippet": "摘要内容..."
            },
            ...
        ]
    """
    if not settings.BAIDU_API_KEY or not settings.BAIDU_SECRET_KEY:
        logger.warning("百度搜索 API 未配置，跳过回退搜索")
        return []
    
    try:
        logger.info(f"调用百度搜索 API: {query}")
        
        # 百度搜索 API 示例（实际 API 可能不同，这里仅演示）
        # 注：百度搜索 API 需要企业认证，这里使用简化版演示
        
        # 模拟搜索结果（实际应调用真实 API）
        mock_results = [
            {
                "title": f"关于 {query} 的搜索结果 1",
                "url": f"https://example.com/search/1?q={query}",
                "snippet": f"这是关于 {query} 的相关内容摘要..."
            },
            {
                "title": f"关于 {query} 的搜索结果 2",
                "url": f"https://example.com/search/2?q={query}",
                "snippet": f"更多关于 {query} 的信息..."
            },
            {
                "title": f"关于 {query} 的搜索结果 3",
                "url": f"https://example.com/search/3?q={query}",
                "snippet": f"{query} 相关的详细介绍..."
            }
        ]
        
        logger.info(f"百度搜索返回 {len(mock_results)} 条结果")
        
        return mock_results[:top_k]
    
    except Exception as e:
        logger.error(f"百度搜索 API 调用失败: {e}")
        return []


def search_baidu_real(query: str, api_key: str, secret_key: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    真实的百度搜索 API 调用（需要企业认证）
    
    注：这里提供接口框架，实际需要根据百度 API 文档实现
    """
    # 1. 获取 Access Token
    token_url = "https://aip.baidubce.com/oauth/2.0/token"
    token_params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    
    try:
        token_response = requests.post(token_url, params=token_params, timeout=10)
        token_response.raise_for_status()
        access_token = token_response.json().get("access_token")
        
        if not access_token:
            logger.error("获取百度 Access Token 失败")
            return []
        
        # 2. 调用搜索 API
        search_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/search"
        search_params = {
            "access_token": access_token
        }
        
        search_payload = {
            "query": query,
            "top_k": top_k
        }
        
        search_response = requests.post(
            search_url,
            params=search_params,
            json=search_payload,
            timeout=10
        )
        
        search_response.raise_for_status()
        result = search_response.json()
        
        # 3. 解析结果
        results = []
        for item in result.get("items", [])[:top_k]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("snippet", "")
            })
        
        return results
    
    except Exception as e:
        logger.error(f"百度搜索 API 调用失败: {e}")
        return []

