"""
SQLAlchemy 数据模型
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import hashlib

from config import settings

Base = declarative_base()
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


class User(Base):
    """用户表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100))
    role = Column(String(20), default='user')  # user, admin
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    logs = relationship("QueryLog", back_populates="user", cascade="all, delete-orphan")


class Article(Base):
    """文章表"""
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    url_hash = Column(String(64), unique=True, nullable=False, index=True)
    source = Column(String(200))
    author = Column(String(100))
    published_at = Column(DateTime)
    crawled_at = Column(DateTime, default=datetime.utcnow)
    
    # 向量化状态
    is_vectorized = Column(Boolean, default=False)
    chunk_count = Column(Integer, default=0)
    
    # 分类与标签
    category = Column(String(100))
    tags = Column(Text)  # JSON 数组字符串
    
    # 统计
    view_count = Column(Integer, default=0)
    reference_count = Column(Integer, default=0)
    
    # 软删除
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    chunks = relationship("Chunk", back_populates="article", cascade="all, delete-orphan")
    
    @staticmethod
    def generate_url_hash(url: str) -> str:
        """生成 URL 哈希"""
        return hashlib.sha256(url.encode()).hexdigest()
    
    __table_args__ = (
        Index('idx_published_at', 'published_at'),
        Index('idx_is_vectorized', 'is_vectorized'),
        Index('idx_category', 'category'),
    )


class Chunk(Base):
    """文章切分块表"""
    __tablename__ = 'chunks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('articles.id', ondelete='CASCADE'), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # 块在文章中的序号
    token_count = Column(Integer)
    
    # FAISS 索引 ID（与 FAISS 中的 ID 对应）
    embedding_id = Column(Integer, unique=True, nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    article = relationship("Article", back_populates="chunks")
    
    __table_args__ = (
        Index('idx_article_chunk', 'article_id', 'chunk_index'),
    )


class QueryLog(Base):
    """查询日志表"""
    __tablename__ = 'query_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    query = Column(Text, nullable=False)
    answer = Column(Text)
    
    # RAG 信息
    retrieved_chunks = Column(Text)  # JSON: chunk IDs
    retrieval_scores = Column(Text)  # JSON: scores
    rerank_scores = Column(Text)     # JSON: rerank scores
    retrieval_method = Column(String(50))  # faiss, fallback, hybrid
    
    # LLM 信息
    llm_model = Column(String(100))
    llm_response_time = Column(Float)  # 秒
    
    # 用户反馈
    user_feedback = Column(String(20))  # positive, negative
    feedback_comment = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    user = relationship("User", back_populates="logs")


class SystemMeta(Base):
    """系统元数据表"""
    __tablename__ = 'system_meta'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    description = Column(String(500))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

