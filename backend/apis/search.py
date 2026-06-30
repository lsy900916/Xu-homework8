"""
RAG 问答 API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from loguru import logger

from core.rag import get_rag_pipeline
from services.search_fallback import search_fallback
from db.models import SessionLocal
from db.dao import QueryLogDAO
from config import settings
import json

search_bp = Blueprint('search', __name__)


@search_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask_question():
    """
    RAG 问答
    
    请求体:
    {
        "question": "最近关于 AI 的新闻有哪些？",
        "top_k": 5,
        "enable_rerank": true,
        "enable_fallback": true
    }
    
    响应:
    {
        "code": 0,
        "data": {
            "question": "...",
            "answer": "...",
            "sources": [...],
            "retrieval_stats": {...},
            "llm_stats": {...},
            "fallback_used": false
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        question = data.get('question', '').strip()
        top_k = data.get('top_k', settings.RAG_RERANK_TOP_K)
        enable_rerank = data.get('enable_rerank', True)
        enable_fallback = data.get('enable_fallback', settings.ENABLE_FALLBACK_SEARCH)
        
        if not question:
            return jsonify({
                'code': 40000,
                'message': '问题不能为空',
                'data': None
            }), 400
        
        logger.info(f"用户 {user_id} 提问: {question}")
        
        # ==================== RAG 查询 ====================
        rag_pipeline = get_rag_pipeline()
        result = rag_pipeline.query(
            question=question,
            top_k=top_k,
            enable_rerank=enable_rerank
        )
        
        fallback_used = False
        
        # ==================== 回退搜索（如需要）====================
        if enable_fallback:
            retrieval_count = result['retrieval_stats']['total_retrieved']
            avg_score = result['retrieval_stats'].get('avg_retrieval_score', 0)
            
            # 触发条件：结果少于阈值 或 平均得分低
            if retrieval_count < settings.FALLBACK_MIN_RESULTS or avg_score < settings.RAG_SIMILARITY_THRESHOLD:
                logger.warning(f"触发回退搜索（结果数: {retrieval_count}, 平均分: {avg_score:.3f}）")
                
                try:
                    fallback_results = search_fallback(question)
                    
                    if fallback_results:
                        fallback_used = True
                        
                        # 合并到 sources
                        for fb_result in fallback_results[:3]:
                            result['sources'].append({
                                'chunk_id': None,
                                'text': fb_result.get('snippet', ''),
                                'article_title': fb_result.get('title', ''),
                                'article_url': fb_result.get('url', ''),
                                'retrieval_score': None,
                                'rerank_score': None,
                                'source_type': 'fallback'
                            })
                        
                        # 重新生成答案（包含回退内容）
                        from core.llm import get_llm
                        llm = get_llm()
                        
                        fallback_context = "\n\n".join([
                            f"[网络来源] {item['title']}\n{item.get('snippet', '')}"
                            for item in fallback_results[:3]
                        ])
                        
                        combined_prompt = f"""请基于以下信息回答用户问题。

本地新闻内容：
{result.get('answer', '未找到相关本地内容')}

网络搜索补充：
{fallback_context}

用户问题：{question}

请综合本地内容和网络搜索结果，给出准确答案。

答案："""
                        
                        llm_result = llm.generate(combined_prompt)
                        result['answer'] = llm_result['text']
                        result['llm_stats']['response_time'] += llm_result['response_time']
                
                except Exception as e:
                    logger.error(f"回退搜索失败: {e}")
                    # 失败不影响主流程
        
        # ==================== 保存查询日志 ====================
        db = SessionLocal()
        try:
            QueryLogDAO.create(
                db,
                user_id=user_id,
                query=question,
                answer=result['answer'],
                retrieved_chunks=json.dumps([s['chunk_id'] for s in result['sources'] if s['chunk_id']]),
                retrieval_scores=json.dumps([s.get('retrieval_score') for s in result['sources']]),
                rerank_scores=json.dumps([s.get('rerank_score') for s in result['sources']]),
                retrieval_method='hybrid' if fallback_used else result['retrieval_stats']['method'],
                llm_model=result['llm_stats'].get('model'),
                llm_response_time=result['llm_stats'].get('response_time')
            )
        finally:
            db.close()
        
        # ==================== 返回结果 ====================
        result['question'] = question
        result['fallback_used'] = fallback_used
        
        return jsonify({
            'code': 0,
            'data': result
        }), 200
    
    except Exception as e:
        logger.error(f"RAG 问答失败: {e}")
        return jsonify({
            'code': 50000,
            'message': f'问答失败: {str(e)}',
            'data': None
        }), 500


@search_bp.route('/fallback-search', methods=['GET'])
def fallback_search_api():
    """
    回退搜索 API（仅后端内部与 n8n 使用）
    
    查询参数:
    ?q=查询词
    
    响应:
    {
        "code": 0,
        "data": {
            "results": [
                {
                    "title": "...",
                    "url": "...",
                    "snippet": "..."
                }
            ]
        }
    }
    """
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'code': 40000,
                'message': '查询词不能为空',
                'data': None
            }), 400
        
        results = search_fallback(query)
        
        return jsonify({
            'code': 0,
            'data': {
                'query': query,
                'results': results
            }
        }), 200
    
    except Exception as e:
        logger.error(f"回退搜索失败: {e}")
        return jsonify({
            'code': 50000,
            'message': f'搜索失败: {str(e)}',
            'data': None
        }), 500

