"""
入库 Skill：封装新闻数据入库和去重功能
"""
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime
import hashlib

from core.embeddings import get_embedding_model
from core.vectorstore import get_vector_store
from db.dao import ArticleDAO, ChunkDAO
from db.models import SessionLocal
from config import settings
from .base_skill import BaseSkill


class IngestionSkill(BaseSkill):
    """入库 Skill：封装新闻数据入库和去重功能"""
    
    def __init__(self):
        super().__init__()
        self.embedding_model = get_embedding_model()
        self.vector_store = get_vector_store()
        self.chunk_size = settings.RAG_CHUNK_SIZE
        self.chunk_overlap = settings.RAG_CHUNK_OVERLAP
    
    def ingest_structured(self, data: Dict, source: str = 'unknown') -> Dict[str, Any]:
        """
        结构化数据入库
        
        Args:
            data: 结构化数据
            source: 数据源
        
        Returns:
            入库结果
        """
        logger.info(f"入库 Skill 执行结构化入库: source={source}")
        
        required_fields = ['title', 'url', 'content']
        if not all(field in data for field in required_fields):
            return {"success": False, "error": "缺少必要字段"}
        
        # 去重检测
        if self.deduplicate(data['url']):
            return {"success": False, "error": "URL 已存在"}
        
        db = SessionLocal()
        try:
            # 创建文章
            article = ArticleDAO.create(
                db,
                title=data['title'],
                url=data['url'],
                content=data.get('content', ''),
                category=data.get('category', 'news'),
                source=source,
                published_at=data.get('published_at') or datetime.utcnow(),
                author=data.get('author'),
                summary=data.get('summary')
            )
            
            # 分块并向量化
            chunks = self._chunk_text(data.get('content', ''))
            embedding_ids = self._vectorize_and_store(chunks, article.id)
            
            # 更新文章状态
            ArticleDAO.update_vectorized_status(db, article.id, len(chunks))
            
            logger.info(f"结构化数据入库成功: article_id={article.id}, chunks={len(chunks)}")
            
            return {
                "success": True,
                "article_id": article.id,
                "chunk_count": len(chunks),
                "embedding_ids": embedding_ids
            }
        
        except Exception as e:
            logger.error(f"结构化数据入库失败: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
        
        finally:
            db.close()
    
    def ingest_unstructured(self, text: str, source: str = 'unknown') -> Dict[str, Any]:
        """
        非结构化数据入库
        
        Args:
            text: 文本内容
            source: 数据源
        
        Returns:
            入库结果
        """
        logger.info(f"入库 Skill 执行非结构化入库: source={source}, 文本长度={len(text)}")
        
        if not text.strip():
            return {"success": False, "error": "文本内容为空"}
        
        db = SessionLocal()
        try:
            # 生成唯一 URL（非结构化数据）
            content_hash = hashlib.md5(text.encode()).hexdigest()
            url = f"internal://{source}/{content_hash}"
            
            # 去重检测
            if self.deduplicate(url, content_hash):
                return {"success": False, "error": "内容已存在"}
            
            # 创建文章
            article = ArticleDAO.create(
                db,
                title=f"从 {source} 导入的内容",
                url=url,
                content=text,
                category='news',
                source=source,
                published_at=datetime.utcnow()
            )
            
            # 分块并向量化
            chunks = self._chunk_text(text)
            embedding_ids = self._vectorize_and_store(chunks, article.id)
            
            # 更新文章状态
            ArticleDAO.update_vectorized_status(db, article.id, len(chunks))
            
            logger.info(f"非结构化数据入库成功: article_id={article.id}, chunks={len(chunks)}")
            
            return {
                "success": True,
                "article_id": article.id,
                "chunk_count": len(chunks),
                "embedding_ids": embedding_ids
            }
        
        except Exception as e:
            logger.error(f"非结构化数据入库失败: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
        
        finally:
            db.close()
    
    def batch_ingest(self, data_list: List[Dict], source: str = 'unknown') -> Dict[str, Any]:
        """
        批量入库
        
        Args:
            data_list: 数据列表
            source: 数据源
        
        Returns:
            批量结果
        """
        logger.info(f"入库 Skill 执行批量入库: source={source}, 数量={len(data_list)}")
        
        success_count = 0
        failed_count = 0
        results = []
        
        for data in data_list:
            try:
                if 'content' in data and 'url' in data and 'title' in data:
                    result = self.ingest_structured(data, source)
                else:
                    text = data.get('text', data.get('content', ''))
                    result = self.ingest_unstructured(text, source)
                
                results.append(result)
                
                if result.get('success'):
                    success_count += 1
                else:
                    failed_count += 1
                
            except Exception as e:
                logger.error(f"批量入库单条失败: {e}")
                results.append({"success": False, "error": str(e)})
                failed_count += 1
        
        logger.info(f"批量入库完成: 成功={success_count}, 失败={failed_count}")
        
        return {
            "success": failed_count == 0,
            "total": len(data_list),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results
        }
    
    def deduplicate(self, url: str, content_hash: str = None) -> bool:
        """
        去重检测
        
        Args:
            url: URL
            content_hash: 内容哈希
        
        Returns:
            是否重复
        """
        db = SessionLocal()
        try:
            # 检查 URL 是否已存在
            article = ArticleDAO.get_by_url(db, url)
            if article:
                logger.debug(f"URL 已存在: {url}")
                return True
            
            return False
        
        finally:
            db.close()
    
    def _chunk_text(self, text: str) -> List[str]:
        """文本分块"""
        if not text:
            return []
        
        chunks = []
        text_length = len(text)
        chunk_size = self.chunk_size
        overlap = self.chunk_overlap
        
        start = 0
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end]
            chunks.append(chunk)
            
            if end >= text_length:
                break
            
            start = end - overlap
        
        logger.debug(f"文本分块完成: {len(chunks)} 块")
        
        return chunks
    
    def _vectorize_and_store(self, chunks: List[str], article_id: int) -> List[int]:
        """向量化并存储"""
        if not chunks:
            return []
        
        # 获取下一个可用的 Embedding ID
        db = SessionLocal()
        try:
            next_embedding_id = ChunkDAO.get_next_embedding_id(db)
        finally:
            db.close()
        
        # 向量化
        vectors = self.embedding_model.encode_batch(chunks)
        
        # 生成 IDs
        embedding_ids = list(range(next_embedding_id, next_embedding_id + len(chunks)))
        
        # 添加到 FAISS
        self.vector_store.add(
            vectors=vectors,
            ids=embedding_ids,
            metadata=[
                {"article_id": article_id, "chunk_index": i}
                for i in range(len(chunks))
            ]
        )
        
        # 创建 Chunk 记录
        db = SessionLocal()
        try:
            chunk_records = [
                {
                    "article_id": article_id,
                    "chunk_index": i,
                    "chunk_text": chunk,
                    "embedding_id": embedding_ids[i],
                    "chunk_hash": hashlib.md5(chunk.encode()).hexdigest()
                }
                for i, chunk in enumerate(chunks)
            ]
            ChunkDAO.create_batch(db, chunk_records)
        finally:
            db.close()
        
        return embedding_ids
    
    def execute(self, **kwargs) -> Any:
        """执行技能"""
        action = kwargs.get('action', 'batch_ingest')
        
        if action == 'ingest_structured':
            return self.ingest_structured(
                data=kwargs['data'],
                source=kwargs.get('source', 'unknown')
            )
        elif action == 'ingest_unstructured':
            return self.ingest_unstructured(
                text=kwargs['text'],
                source=kwargs.get('source', 'unknown')
            )
        elif action == 'batch_ingest':
            return self.batch_ingest(
                data_list=kwargs['data_list'],
                source=kwargs.get('source', 'unknown')
            )
        elif action == 'deduplicate':
            return self.deduplicate(
                url=kwargs['url'],
                content_hash=kwargs.get('content_hash')
            )
        
        return {"error": f"不支持的操作: {action}"}
