"""
数据入库 API：结构化（Excel/JSON）与非结构化（文本/HTML）
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
import pandas as pd
from bs4 import BeautifulSoup
import html2text
from typing import List, Dict, Any
import re

from db.models import SessionLocal
from db.dao import ArticleDAO, ChunkDAO
from core.embeddings import get_embedding_model
from core.vectorstore import get_vector_store
from config import settings

ingest_bp = Blueprint('ingest', __name__)


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    文本切分
    
    Args:
        text: 原始文本
        chunk_size: 块大小（字符）
        overlap: 重叠大小
        
    Returns:
        List[str]: 切分后的文本块
    """
    chunk_size = chunk_size or settings.RAG_CHUNK_SIZE
    overlap = overlap or settings.RAG_CHUNK_OVERLAP
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    
    return chunks


def extract_from_html(html_content: str) -> Dict[str, str]:
    """
    从 HTML 提取内容
    
    Returns:
        {
            "title": "...",
            "content": "...",
            "author": "...",
            "published_at": "..."
        }
    """
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 提取标题
    title = ""
    if soup.find('h1'):
        title = soup.find('h1').get_text(strip=True)
    elif soup.find('title'):
        title = soup.find('title').get_text(strip=True)
    
    # 提取正文（使用 html2text）
    h = html2text.HTML2Text()
    h.ignore_links = False
    content = h.handle(html_content)
    content = re.sub(r'\n\n+', '\n\n', content)  # 压缩多个换行
    
    return {
        "title": title,
        "content": content.strip(),
        "author": "",
        "published_at": None
    }


@ingest_bp.route('/structured', methods=['POST'])
@jwt_required()
def ingest_structured():
    """
    结构化数据入库（Excel/JSON）
    
    请求体（JSON）:
    {
        "data": [
            {
                "title": "新闻标题",
                "content": "新闻正文...",
                "url": "https://example.com/news/1",
                "source": "新闻来源",
                "author": "作者",
                "published_at": "2026-6-30T10:00:00Z",
                "category": "科技"
            }
        ]
    }
    
    或上传 Excel 文件（multipart/form-data）
    
    响应:
    {
        "code": 0,
        "message": "入库成功",
        "data": {
            "total": 10,
            "success": 9,
            "failed": 1,
            "details": [...]
        }
    }
    """
    try:
        data_list = []
        
        # 处理 JSON 格式
        if request.is_json:
            data = request.get_json()
            data_list = data.get('data', [])
        
        # 处理 Excel 上传
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
                data_list = df.to_dict('records')
            else:
                return jsonify({
                    'code': 40000,
                    'message': '不支持的文件格式',
                    'data': None
                }), 400
        
        else:
            return jsonify({
                'code': 40000,
                'message': '请提供 JSON 数据或上传 Excel 文件',
                'data': None
            }), 400
        
        if not data_list:
            return jsonify({
                'code': 40000,
                'message': '数据为空',
                'data': None
            }), 400
        
        # 批量入库
        result = batch_ingest(data_list)
        
        return jsonify({
            'code': 0,
            'message': '入库完成',
            'data': result
        }), 200
    
    except Exception as e:
        logger.error(f"结构化数据入库失败: {e}")
        return jsonify({
            'code': 50000,
            'message': f'入库失败: {str(e)}',
            'data': None
        }), 500


@ingest_bp.route('/unstructured', methods=['POST'])
@jwt_required()
def ingest_unstructured():
    """
    非结构化数据入库（纯文本/HTML）
    
    请求体:
    {
        "content": "HTML 或纯文本内容",
        "url": "https://example.com/news/1",
        "type": "html",  // html, text
        "source": "新闻来源"
    }
    
    响应:
    {
        "code": 0,
        "message": "入库成功 | 部分成功 | 全部已存在，无需入库",
        "data": {
            "total": 1,
            "success": 1,
            "skipped": 0,
            "failed": 0,
            "details": [
                { "url": "...", "status": "success|skipped|failed", "reason": "..." }
            ]
        }
    }
    """
    try:
        data = request.get_json()
        
        content = data.get('content')
        url = data.get('url')
        content_type = data.get('type', 'text')
        source = data.get('source', '')
        
        if not content or not url:
            return jsonify({
                'code': 40000,
                'message': 'content 和 url 不能为空',
                'data': None
            }), 400
        
        # 提取内容
        if content_type == 'html':
            extracted = extract_from_html(content)
            title = extracted['title']
            clean_content = extracted['content']
        else:
            # 纯文本，尝试提取标题（第一行）
            lines = content.split('\n', 1)
            title = lines[0].strip() if lines else "无标题"
            clean_content = lines[1].strip() if len(lines) > 1 else content
        
        # 构建文章数据
        article_data = {
            'title': title,
            'content': clean_content,
            'url': url,
            'source': source
        }
        
        # 入库
        result = batch_ingest([article_data])
        
        # 根据结果生成更准确的 message 和 code
        total = result.get('total', 0)
        success = result.get('success', 0)
        skipped = result.get('skipped', 0)
        failed = result.get('failed', 0)
        
        if success > 0 and failed == 0:
            message = '入库成功'
            code = 0
        elif success > 0 and (failed > 0 or skipped > 0):
            message = '部分成功'
            code = 0
        elif success == 0 and skipped == total and total > 0:
            message = '全部已存在，无需入库'
            code = 0
        else:
            message = '入库失败'
            code = 40000
        
        return jsonify({
            'code': code,
            'message': message,
            'data': result
        }), 200
    
    except Exception as e:
        logger.error(f"非结构化数据入库失败: {e}")
        return jsonify({
            'code': 50000,
            'message': f'入库失败: {str(e)}',
            'data': None
        }), 500


def batch_ingest(data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    批量入库核心逻辑
    
    流程:
    1. 去重检查
    2. 插入 articles 表
    3. 文本切分
    4. 生成向量
    5. 插入 chunks 表
    6. 更新 FAISS 索引
    
    Returns:
        {
            "total": 10,
            "success": 9,
            "failed": 1,
            "details": [...]
        }
    """
    db = SessionLocal()
    embedding_model = get_embedding_model()
    vector_store = get_vector_store()
    
    total = len(data_list)
    success = 0
    skipped = 0
    failed = 0
    details = []
    
    try:
        for item in data_list:
            try:
                title = item.get('title', '')
                content = item.get('content', '')
                url = item.get('url', '')
                
                if not title or not content or not url:
                    details.append({
                        'url': url,
                        'status': 'failed',
                        'reason': '缺少必填字段'
                    })
                    failed += 1
                    continue
                
                # 去重检查
                existing = ArticleDAO.get_by_url(db, url)
                if existing:
                    details.append({
                        'url': url,
                        'status': 'skipped',
                        'reason': '已存在'
                    })
                    skipped += 1
                    continue
                
                # 创建文章记录
                article = ArticleDAO.create(
                    db,
                    title=title,
                    content=content,
                    url=url,
                    source=item.get('source'),
                    author=item.get('author'),
                    published_at=item.get('published_at'),
                    category=item.get('category')
                )
                
                # 文本切分
                chunks_text = chunk_text(content)
                
                # 生成向量
                chunk_vectors = embedding_model.encode_batch(chunks_text)
                
                # 获取下一个可用的 embedding_id
                next_embedding_id = ChunkDAO.get_next_embedding_id(db)
                
                # 构建 chunks 数据
                chunks_data = []
                embedding_ids = []
                
                for i, (chunk_text_value, vector) in enumerate(zip(chunks_text, chunk_vectors)):
                    embedding_id = next_embedding_id + i
                    chunks_data.append({
                        'article_id': article.id,
                        'chunk_text': chunk_text_value,
                        'chunk_index': i,
                        'token_count': len(chunk_text_value.split()),
                        'embedding_id': embedding_id
                    })
                    embedding_ids.append(embedding_id)
                
                # 插入 chunks
                ChunkDAO.create_batch(db, chunks_data)
                
                # 添加到 FAISS
                vector_store.add(
                    vectors=chunk_vectors,
                    ids=embedding_ids
                )
                
                # 更新文章向量化状态
                ArticleDAO.update_vectorized_status(db, article.id, len(chunks_text))
                
                details.append({
                    'url': url,
                    'status': 'success',
                    'article_id': article.id,
                    'chunks_count': len(chunks_text)
                })
                success += 1
                
                logger.info(f"文章入库成功: {title} ({len(chunks_text)} chunks)")
            
            except Exception as e:
                logger.error(f"单条数据入库失败: {e}")
                details.append({
                    'url': item.get('url', ''),
                    'status': 'failed',
                    'reason': str(e)
                })
                failed += 1
    
    finally:
        db.close()
    
    return {
        'total': total,
        'success': success,
        'skipped': skipped,
        'failed': failed,
        'details': details
    }

