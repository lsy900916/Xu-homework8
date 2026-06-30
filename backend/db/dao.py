"""
数据访问对象（DAO）
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import json

from db.models import User, Article, Chunk, QueryLog, SystemMeta


class UserDAO:
    """用户 DAO"""
    
    @staticmethod
    def create(db: Session, email: str, password_hash: str, username: str = None) -> User:
        """创建用户"""
        user = User(email=email, password_hash=password_hash, username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def increment_failed_login(db: Session, user: User):
        """增加登录失败次数"""
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.is_locked = True
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        db.commit()
    
    @staticmethod
    def reset_failed_login(db: Session, user: User):
        """重置登录失败次数"""
        user.failed_login_attempts = 0
        user.is_locked = False
        user.locked_until = None
        db.commit()


class ArticleDAO:
    """文章 DAO"""
    
    @staticmethod
    def create(db: Session, **kwargs) -> Article:
        """创建文章"""
        url_hash = Article.generate_url_hash(kwargs['url'])
        article = Article(url_hash=url_hash, **kwargs)
        db.add(article)
        db.commit()
        db.refresh(article)
        return article
    
    @staticmethod
    def get_by_id(db: Session, article_id: int) -> Optional[Article]:
        """根据 ID 获取文章"""
        return db.query(Article).filter(Article.id == article_id, Article.is_deleted == False).first()
    
    @staticmethod
    def get_by_url(db: Session, url: str) -> Optional[Article]:
        """根据 URL 获取文章"""
        url_hash = Article.generate_url_hash(url)
        return db.query(Article).filter(Article.url_hash == url_hash).first()
    
    @staticmethod
    def get_by_url_hash(db: Session, url_hash: str) -> Optional[Article]:
        """根据 URL Hash 获取文章"""
        return db.query(Article).filter(Article.url_hash == url_hash).first()
    
    @staticmethod
    def list_articles(
        db: Session, 
        page: int = 1, 
        page_size: int = 20,
        category: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Article]:
        """获取文章列表"""
        query = db.query(Article).filter(Article.is_deleted == False)
        
        if category:
            query = query.filter(Article.category == category)
        
        if start_date:
            query = query.filter(Article.published_at >= start_date)
        
        if end_date:
            query = query.filter(Article.published_at <= end_date)
        
        query = query.order_by(desc(Article.published_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        return query.all()
    
    @staticmethod
    def count(db: Session, category: str = None) -> int:
        """统计文章数量"""
        query = db.query(func.count(Article.id)).filter(Article.is_deleted == False)
        if category:
            query = query.filter(Article.category == category)
        return query.scalar()
    
    @staticmethod
    def update_vectorized_status(db: Session, article_id: int, chunk_count: int):
        """更新向量化状态"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if article:
            article.is_vectorized = True
            article.chunk_count = chunk_count
            db.commit()


class ChunkDAO:
    """文章块 DAO"""
    
    @staticmethod
    def create_batch(db: Session, chunks: List[Dict[str, Any]]) -> List[Chunk]:
        """批量创建文章块"""
        chunk_objects = [Chunk(**chunk) for chunk in chunks]
        db.add_all(chunk_objects)
        db.commit()
        return chunk_objects
    
    @staticmethod
    def get_by_embedding_ids(db: Session, embedding_ids: List[int]) -> List[Chunk]:
        """根据 Embedding ID 批量获取"""
        return db.query(Chunk).filter(Chunk.embedding_id.in_(embedding_ids)).all()
    
    @staticmethod
    def get_by_article_id(db: Session, article_id: int) -> List[Chunk]:
        """获取文章的所有块"""
        return db.query(Chunk).filter(Chunk.article_id == article_id).order_by(Chunk.chunk_index).all()
    
    @staticmethod
    def get_next_embedding_id(db: Session) -> int:
        """获取下一个可用的 Embedding ID"""
        max_id = db.query(func.max(Chunk.embedding_id)).scalar()
        return (max_id or 0) + 1


class QueryLogDAO:
    """查询日志 DAO"""
    
    @staticmethod
    def create(db: Session, user_id: int, query: str, answer: str, **kwargs) -> QueryLog:
        """创建查询日志"""
        log = QueryLog(user_id=user_id, query=query, answer=answer, **kwargs)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def get_user_logs(db: Session, user_id: int, page: int = 1, page_size: int = 20) -> List[QueryLog]:
        """获取用户查询历史"""
        return db.query(QueryLog)\
            .filter(QueryLog.user_id == user_id)\
            .order_by(desc(QueryLog.created_at))\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()


class SystemMetaDAO:
    """系统元数据 DAO"""
    
    @staticmethod
    def get(db: Session, key: str) -> Optional[str]:
        """获取元数据值"""
        meta = db.query(SystemMeta).filter(SystemMeta.key == key).first()
        return meta.value if meta else None
    
    @staticmethod
    def set(db: Session, key: str, value: str, description: str = None):
        """设置元数据"""
        meta = db.query(SystemMeta).filter(SystemMeta.key == key).first()
        if meta:
            meta.value = value
            meta.updated_at = datetime.utcnow()
            if description:
                meta.description = description
        else:
            meta = SystemMeta(key=key, value=value, description=description)
            db.add(meta)
        db.commit()

