"""
聚类分析报告、关键词 Top10 API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import jieba
import re

from db.models import SessionLocal
from db.dao import ArticleDAO, ChunkDAO
from core.vectorstore import get_vector_store
from config import settings

reports_bp = Blueprint('reports', __name__)


def extract_keywords_tfidf(texts: List[str], top_k: int = 10) -> List[Dict[str, Any]]:
    """
    使用 TF-IDF 提取关键词
    
    Returns:
        [{"word": "AI", "score": 0.85}, ...]
    """
    # 中文分词
    jieba.setLogLevel(jieba.logging.INFO)
    
    # 停用词
    stopwords = set(['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'])
    
    def tokenize(text):
        words = jieba.cut(text)
        return [w for w in words if len(w) > 1 and w not in stopwords]
    
    # TF-IDF
    vectorizer = TfidfVectorizer(
        tokenizer=tokenize,
        max_features=100,
        max_df=0.8,
        min_df=2
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        
        # 计算每个词的平均 TF-IDF 得分
        scores = tfidf_matrix.mean(axis=0).A1
        
        # 排序
        word_scores = [(feature_names[i], scores[i]) for i in range(len(feature_names))]
        word_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {"word": word, "score": float(score)}
            for word, score in word_scores[:top_k]
        ]
    
    except Exception as e:
        logger.error(f"关键词提取失败: {e}")
        return []


@reports_bp.route('/clusters', methods=['GET'])
@jwt_required()
def cluster_analysis():
    """
    聚类分析
    
    查询参数:
    ?start_date=2025-10-01&end_date=2026-6-30&n_clusters=5&algorithm=kmeans
    
    响应:
    {
        "code": 0,
        "data": {
            "total_news": 100,
            "n_clusters": 5,
            "clusters": [
                {
                    "cluster_id": 0,
                    "size": 25,
                    "keywords": ["AI", "技术", "发展"],
                    "sample_titles": ["...", "..."]
                }
            ],
            "visualization": {
                "coordinates": [
                    {"x": 0.5, "y": 0.3, "cluster_id": 0, "article_id": 1},
                    ...
                ]
            }
        }
    }
    """
    try:
        # 参数解析
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        n_clusters = int(request.args.get('n_clusters', settings.CLUSTER_N_CLUSTERS))
        algorithm = request.args.get('algorithm', settings.CLUSTER_ALGORITHM)
        
        # 日期解析
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str)
        else:
            start_date = datetime.now() - timedelta(days=7)
        
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str)
        else:
            end_date = datetime.now()
        
        logger.info(f"开始聚类分析: {start_date} ~ {end_date}, n_clusters={n_clusters}")
        
        db = SessionLocal()
        vector_store = get_vector_store()
        
        try:
            # 获取指定时间范围的文章
            articles = ArticleDAO.list_articles(
                db,
                page=1,
                page_size=10000,  # 大数量
                start_date=start_date,
                end_date=end_date
            )
            
            if len(articles) < n_clusters:
                return jsonify({
                    'code': 40000,
                    'message': f'文章数量（{len(articles)}）少于聚类数（{n_clusters}）',
                    'data': None
                }), 400
            
            # 收集向量
            article_ids = [a.id for a in articles]
            vectors = []
            valid_articles = []
            
            for article in articles:
                chunks = ChunkDAO.get_by_article_id(db, article.id)
                if chunks:
                    # 使用第一个 chunk 的向量代表文章
                    # TODO: 更好的方式是平均所有 chunks 的向量
                    embedding_id = chunks[0].embedding_id
                    # 从 FAISS 获取向量（这里简化，实际需要实现 get_vector_by_id）
                    # 暂时跳过，使用随机向量演示
                    vectors.append(np.random.rand(settings.EMBEDDING_DIMENSION))
                    valid_articles.append(article)
            
            vectors = np.array(vectors).astype('float32')
            
            # 聚类
            if algorithm == 'kmeans':
                clusterer = KMeans(n_clusters=n_clusters, random_state=42)
            elif algorithm == 'dbscan':
                clusterer = DBSCAN(eps=0.5, min_samples=2)
            else:
                return jsonify({
                    'code': 40000,
                    'message': f'不支持的算法: {algorithm}',
                    'data': None
                }), 400
            
            labels = clusterer.fit_predict(vectors)
            
            # 构建聚类结果
            clusters = []
            for cluster_id in range(n_clusters):
                cluster_articles = [valid_articles[i] for i, label in enumerate(labels) if label == cluster_id]
                
                if not cluster_articles:
                    continue
                
                # 提取关键词
                texts = [a.content for a in cluster_articles]
                keywords_data = extract_keywords_tfidf(texts, top_k=10)
                keywords = [kw['word'] for kw in keywords_data[:5]]
                
                clusters.append({
                    'cluster_id': cluster_id,
                    'size': len(cluster_articles),
                    'keywords': keywords,
                    'sample_titles': [a.title for a in cluster_articles[:5]]
                })
            
            # 可视化（t-SNE 降维到 2D）
            tsne = TSNE(n_components=2, random_state=42)
            coords_2d = tsne.fit_transform(vectors)
            
            visualization = {
                'coordinates': [
                    {
                        'x': float(coords_2d[i][0]),
                        'y': float(coords_2d[i][1]),
                        'cluster_id': int(labels[i]),
                        'article_id': valid_articles[i].id,
                        'title': valid_articles[i].title
                    }
                    for i in range(len(valid_articles))
                ]
            }
            
            logger.info(f"聚类分析完成，共 {len(valid_articles)} 篇文章，{n_clusters} 个聚类")
            
            return jsonify({
                'code': 0,
                'data': {
                    'total_news': len(valid_articles),
                    'n_clusters': n_clusters,
                    'algorithm': algorithm,
                    'clusters': clusters,
                    'visualization': visualization
                }
            }), 200
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"聚类分析失败: {e}")
        return jsonify({
            'code': 50000,
            'message': f'聚类分析失败: {str(e)}',
            'data': None
        }), 500


@reports_bp.route('/topkeywords', methods=['GET'])
@jwt_required()
def top_keywords():
    """
    关键词 Top10
    
    查询参数:
    ?time_range=daily&start_date=2026-6-30&category=科技
    
    响应:
    {
        "code": 0,
        "data": {
            "time_range": "daily",
            "start_date": "2026-6-30",
            "end_date": "2026-6-30",
            "keywords": [
                {"word": "AI", "count": 156},
                {"word": "技术", "count": 89},
                ...
            ]
        }
    }
    """
    try:
        time_range = request.args.get('time_range', 'daily')  # daily, weekly, monthly
        start_date_str = request.args.get('start_date')
        category = request.args.get('category')
        
        # 计算日期范围
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str)
        else:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if time_range == 'daily':
            end_date = start_date + timedelta(days=1)
        elif time_range == 'weekly':
            end_date = start_date + timedelta(weeks=1)
        elif time_range == 'monthly':
            end_date = start_date + timedelta(days=30)
        else:
            return jsonify({
                'code': 40000,
                'message': '不支持的 time_range',
                'data': None
            }), 400
        
        logger.info(f"统计关键词: {start_date} ~ {end_date}")
        
        db = SessionLocal()
        try:
            # 获取文章
            articles = ArticleDAO.list_articles(
                db,
                page=1,
                page_size=10000,
                category=category,
                start_date=start_date,
                end_date=end_date
            )
            
            if not articles:
                return jsonify({
                    'code': 0,
                    'data': {
                        'time_range': time_range,
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'keywords': []
                    }
                }), 200
            
            # 提取关键词
            texts = [f"{a.title} {a.content}" for a in articles]
            keywords_data = extract_keywords_tfidf(texts, top_k=10)
            
            # 转换为计数（这里简化，使用 score * 100 作为计数）
            keywords = [
                {
                    'word': kw['word'],
                    'count': int(kw['score'] * 100),
                    'score': kw['score']
                }
                for kw in keywords_data
            ]
            
            logger.info(f"关键词统计完成，共 {len(articles)} 篇文章")
            
            return jsonify({
                'code': 0,
                'data': {
                    'time_range': time_range,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'total_articles': len(articles),
                    'keywords': keywords
                }
            }), 200
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"关键词统计失败: {e}")
        return jsonify({
            'code': 50000,
            'message': f'关键词统计失败: {str(e)}',
            'data': None
        }), 500

