"""
配置文件
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # ==================== 应用基础 ====================
    APP_NAME: str = "XU-News-AI-RAG Backend"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    
    # ==================== 路径配置 ====================
    BASE_DIR: Path = Path(__file__).parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    FAISS_INDEX_PATH: Path = STORAGE_DIR / "faiss_index"
    DB_PATH: Path = STORAGE_DIR / "app.db"
    LOG_DIR: Path = BASE_DIR.parent / "logs"
    
    # ==================== 数据库 ====================
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    
    # ==================== JWT ====================
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES: int = 86400  # 24小时（秒）
    
    # ==================== Ollama ====================
    OLLAMA_HOST: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b"  # 改为你已有的模型
    OLLAMA_TIMEOUT: int = 60
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_MAX_TOKENS: int = 2048
    
    # ==================== Embedding ====================
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384  # all-MiniLM-L6-v2 维度
    EMBEDDING_BATCH_SIZE: int = 32
    
    # ==================== Reranker ====================
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    RERANKER_TOP_K: int = 10  # 重排前保留的候选数
    
    # ==================== RAG ====================
    RAG_RETRIEVAL_TOP_K: int = 20  # 初次召回数量
    RAG_RERANK_TOP_K: int = 5      # 重排后保留数量
    RAG_SIMILARITY_THRESHOLD: float = 0.5  # 相似度阈值
    RAG_CHUNK_SIZE: int = 512      # 切分块大小（字符）
    RAG_CHUNK_OVERLAP: int = 50    # 切分重叠
    
    # ==================== 回退搜索 ====================
    ENABLE_FALLBACK_SEARCH: bool = True
    FALLBACK_MIN_RESULTS: int = 1  # 少于此数量触发回退
    BAIDU_API_KEY: Optional[str] = None
    BAIDU_SECRET_KEY: Optional[str] = None
    
    # ==================== 聚类 ====================
    CLUSTER_N_CLUSTERS: int = 5
    CLUSTER_ALGORITHM: str = "kmeans"  # kmeans, dbscan
    
    # ==================== 安全 ====================
    BCRYPT_ROUNDS: int = 12
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # ==================== 日志 ====================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    # ==================== 邮件配置 ====================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    SENDER_EMAIL: Optional[str] = None
    
    # ==================== CORS ====================
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env.local"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = 'ignore'


# 单例配置对象
settings = Settings()

# 确保必要目录存在
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.FAISS_INDEX_PATH.mkdir(parents=True, exist_ok=True)
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

