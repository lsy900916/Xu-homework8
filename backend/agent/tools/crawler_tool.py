"""
爬虫工具：封装网页抓取功能
"""
from typing import Dict, Any, Optional
from loguru import logger

from services.crawlers import get_crawler_helper
from .base_tool import BaseTool


class CrawlerTool(BaseTool):
    """爬虫工具：封装网页抓取功能"""
    
    def __init__(self):
        super().__init__()
        self.crawler_helper = get_crawler_helper()
    
    def crawl_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        抓取网页
        
        Args:
            url: 目标 URL
            timeout: 超时时间（秒）
        
        Returns:
            网页内容
        """
        logger.info(f"爬虫工具执行网页抓取: {url}")
        
        return self.crawler_helper.fetch_page(url, timeout=timeout)
    
    def check_robots(self, url: str) -> bool:
        """
        检查 robots.txt
        
        Args:
            url: 目标 URL
        
        Returns:
            是否允许抓取
        """
        logger.info(f"爬虫工具检查 robots.txt: {url}")
        
        return self.crawler_helper.check_robots_txt(url)
    
    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """
        提取正文
        
        Args:
            html: HTML 内容
            url: 原始 URL
        
        Returns:
            正文内容
        """
        logger.info(f"爬虫工具提取正文: {url}")
        
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html, 'lxml')
            
            # 移除脚本和样式
            for script in soup(['script', 'style', 'nav', 'header', 'footer']):
                script.decompose()
            
            # 提取标题
            title = soup.title.string if soup.title else ''
            
            # 提取正文（优先使用 article 标签）
            article_tag = soup.find('article')
            if article_tag:
                content = article_tag.get_text(strip=True)
            else:
                content = soup.get_text(strip=True)
            
            # 提取图片
            images = []
            for img in soup.find_all('img'):
                img_url = img.get('src', '')
                if img_url:
                    images.append(img_url)
            
            return {
                "title": title,
                "content": content,
                "images": images[:10],
                "url": url
            }
        
        except ImportError:
            logger.error("未安装 BeautifulSoup 库")
            return {"title": "", "content": html, "images": [], "url": url}
        except Exception as e:
            logger.error(f"提取正文失败: {e}")
            return {"title": "", "content": "", "images": [], "url": url}
    
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        action = kwargs.get('action', 'crawl_page')
        
        if action == 'crawl_page':
            return self.crawl_page(
                url=kwargs['url'],
                timeout=kwargs.get('timeout', 10)
            )
        elif action == 'check_robots':
            return self.check_robots(
                url=kwargs['url']
            )
        elif action == 'extract_content':
            return self.extract_content(
                html=kwargs['html'],
                url=kwargs['url']
            )
        
        return {"error": f"不支持的操作: {action}"}
