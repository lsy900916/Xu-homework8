"""
爬虫扩展点（给 n8n 用的内部 API）

注：主要爬取逻辑在 n8n 工作流中实现
此文件提供辅助函数与扩展点
"""
from typing import Dict, Any, Optional
from loguru import logger
import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import time


class CrawlerHelper:
    """爬虫辅助类"""
    
    def __init__(self):
        self.user_agent = "XU-News-Bot/1.0 (+https://xu-news.com/bot; contact@xu-news.com)"
        self.rate_limit = 2  # 秒
        self.last_request_time = {}
    
    def check_robots_txt(self, url: str) -> bool:
        """
        检查 robots.txt 是否允许爬取
        
        Args:
            url: 目标 URL
            
        Returns:
            bool: True 允许，False 禁止
        """
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            robots_url = f"{base_url}/robots.txt"
            
            parser = RobotFileParser()
            parser.set_url(robots_url)
            parser.read()
            
            allowed = parser.can_fetch(self.user_agent, url)
            
            logger.debug(f"robots.txt 检查: {url} -> {'允许' if allowed else '禁止'}")
            
            return allowed
        
        except Exception as e:
            logger.warning(f"robots.txt 检查失败: {e}，默认允许")
            return True  # 失败时默认允许
    
    def rate_limit_wait(self, domain: str):
        """速率限制：等待到允许时间"""
        last_time = self.last_request_time.get(domain, 0)
        elapsed = time.time() - last_time
        
        if elapsed < self.rate_limit:
            sleep_time = self.rate_limit - elapsed
            logger.debug(f"速率限制等待 {sleep_time:.2f}s for {domain}")
            time.sleep(sleep_time)
        
        self.last_request_time[domain] = time.time()
    
    def fetch_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        获取页面 HTML
        
        Args:
            url: 目标 URL
            timeout: 超时时间（秒）
            
        Returns:
            str: HTML 内容，失败返回 None
        """
        # 检查 robots.txt
        if not self.check_robots_txt(url):
            logger.warning(f"robots.txt 禁止爬取: {url}")
            return None
        
        # 速率限制
        domain = urlparse(url).netloc
        self.rate_limit_wait(domain)
        
        try:
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            logger.info(f"成功获取页面: {url} ({len(response.text)} bytes)")
            
            return response.text
        
        except requests.exceptions.RequestException as e:
            logger.error(f"获取页面失败: {url}, 错误: {e}")
            return None
    
    def extract_news_list(self, html: str, config: Dict[str, str]) -> list:
        """
        从列表页提取新闻链接
        
        Args:
            html: 页面 HTML
            config: 提取配置，如 {"link_selector": "a.news-link", "title_selector": "h2.title"}
            
        Returns:
            list: [{"url": "...", "title": "..."}, ...]
        """
        soup = BeautifulSoup(html, 'lxml')
        
        link_selector = config.get('link_selector', 'a')
        title_selector = config.get('title_selector', 'a')
        
        news_list = []
        
        for link_elem in soup.select(link_selector):
            url = link_elem.get('href', '')
            if not url.startswith('http'):
                continue
            
            title_elem = link_elem.select_one(title_selector) or link_elem
            title = title_elem.get_text(strip=True)
            
            news_list.append({
                'url': url,
                'title': title
            })
        
        logger.debug(f"提取到 {len(news_list)} 条新闻链接")
        
        return news_list


# 单例
_crawler_helper = None


def get_crawler_helper() -> CrawlerHelper:
    """获取爬虫辅助单例"""
    global _crawler_helper
    if _crawler_helper is None:
        _crawler_helper = CrawlerHelper()
    return _crawler_helper

