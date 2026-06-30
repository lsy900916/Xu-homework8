-- ==================== XU-News-AI-RAG 数据库初始化脚本 ====================
-- 此文件仅供参考，实际使用 SQLAlchemy 的 Base.metadata.create_all()

-- ==================== 用户表 ====================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT 1,
    failed_login_attempts INTEGER DEFAULT 0,
    is_locked BOOLEAN DEFAULT 0,
    locked_until DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- ==================== 文章表 ====================
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    url VARCHAR(1000) UNIQUE NOT NULL,
    url_hash VARCHAR(64) UNIQUE NOT NULL,
    source VARCHAR(200),
    author VARCHAR(100),
    published_at DATETIME,
    crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    is_vectorized BOOLEAN DEFAULT 0,
    chunk_count INTEGER DEFAULT 0,
    
    category VARCHAR(100),
    tags TEXT,
    
    view_count INTEGER DEFAULT 0,
    reference_count INTEGER DEFAULT 0,
    
    is_deleted BOOLEAN DEFAULT 0,
    deleted_at DATETIME,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_articles_url ON articles(url);
CREATE INDEX idx_articles_url_hash ON articles(url_hash);
CREATE INDEX idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX idx_articles_is_vectorized ON articles(is_vectorized);
CREATE INDEX idx_articles_category ON articles(category);

-- ==================== 文章切分块表 ====================
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    token_count INTEGER,
    embedding_id INTEGER UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE INDEX idx_chunks_article_id ON chunks(article_id);
CREATE INDEX idx_chunks_embedding_id ON chunks(embedding_id);
CREATE INDEX idx_chunks_article_chunk ON chunks(article_id, chunk_index);

-- ==================== 查询日志表 ====================
CREATE TABLE IF NOT EXISTS query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    query TEXT NOT NULL,
    answer TEXT,
    
    retrieved_chunks TEXT,
    retrieval_scores TEXT,
    rerank_scores TEXT,
    retrieval_method VARCHAR(50),
    
    llm_model VARCHAR(100),
    llm_response_time FLOAT,
    
    user_feedback VARCHAR(20),
    feedback_comment TEXT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_query_logs_user_id ON query_logs(user_id);
CREATE INDEX idx_query_logs_created_at ON query_logs(created_at DESC);

-- ==================== 系统元数据表 ====================
CREATE TABLE IF NOT EXISTS system_meta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description VARCHAR(500),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_meta_key ON system_meta(key);

-- ==================== 初始化系统元数据 ====================
INSERT OR IGNORE INTO system_meta (key, value, description) VALUES
('db_version', '1.0.0', '数据库版本'),
('total_vectors', '0', 'FAISS 向量总数'),
('last_backup', '', '最后备份时间');

-- ==================== 创建管理员账户（密码: Admin123，bcrypt 加密）====================
-- 注意：实际使用时应通过程序生成
-- INSERT OR IGNORE INTO users (email, password_hash, username, role) VALUES
-- ('admin@xu-news.com', '$2b$12$...', 'Admin', 'admin');

