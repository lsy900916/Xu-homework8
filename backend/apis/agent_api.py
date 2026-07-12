"""
Agent API 路由：提供统一的 Agent 接口
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from loguru import logger
import time

from agent.news_agent import NewsAgent

agent_bp = Blueprint('agent', __name__)

_news_agent = None


def get_agent() -> NewsAgent:
    """获取 NewsAgent 单例"""
    global _news_agent
    if _news_agent is None:
        _news_agent = NewsAgent()
        logger.info("NewsAgent 初始化完成")
    return _news_agent


@agent_bp.route('/query', methods=['POST'])
@jwt_required()
def agent_query():
    """
    Agent 统一查询接口
    
    请求示例：
    {
        "question": "最近关于人工智能的新闻有哪些？",
        "options": {
            "enable_fallback": true,
            "top_k": 5
        }
    }
    
    响应示例：
    {
        "code": 0,
        "data": {
            "answer": "...",
            "sources": [...],
            "plan": [...],
            "execution_time": 2.3
        },
        "message": "success"
    }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        question = data.get('question', '')
        options = data.get('options', {})
        
        if not question:
            return jsonify({
                'code': 400,
                'message': '问题不能为空',
                'data': None
            }), 400
        
        user_id = get_jwt_identity()
        
        agent = get_agent()
        result = agent.answer_question(question, user_id, options)
        
        execution_time = time.time() - start_time
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                **result,
                'execution_time': round(execution_time, 2)
            }
        })
    
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Agent 查询失败: {e}")
        return jsonify({
            'code': 500,
            'message': 'Agent 查询失败',
            'data': {
                'error': str(e),
                'execution_time': round(execution_time, 2)
            }
        }), 500


@agent_bp.route('/analyze', methods=['POST'])
@jwt_required()
def agent_analyze():
    """
    Agent 分析接口
    
    请求示例：
    {
        "type": "clusters",
        "time_range": "weekly"
    }
    
    响应示例：
    {
        "code": 0,
        "data": {
            "clusters": [...],
            "total_articles": 100
        },
        "message": "success"
    }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        analysis_type = data.get('type', 'clusters')
        time_range = data.get('time_range', 'weekly')
        
        agent = get_agent()
        
        if analysis_type == 'clusters':
            result = agent.analyze_clusters(time_range=time_range)
        elif analysis_type == 'keywords':
            result = agent.analyze_keywords(
                time_range=time_range,
                top_n=data.get('top_n', 10)
            )
        elif analysis_type == 'trend':
            keyword = data.get('keyword', '')
            if not keyword:
                return jsonify({
                    'code': 400,
                    'message': '关键词不能为空',
                    'data': None
                }), 400
            analysis_skill = agent.skills.get('analysis')
            result = analysis_skill.trend_analysis(keyword=keyword, time_range=time_range)
        else:
            return jsonify({
                'code': 400,
                'message': '不支持的分析类型',
                'data': None
            }), 400
        
        execution_time = time.time() - start_time
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                **result,
                'execution_time': round(execution_time, 2)
            }
        })
    
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Agent 分析失败: {e}")
        return jsonify({
            'code': 500,
            'message': 'Agent 分析失败',
            'data': {
                'error': str(e),
                'execution_time': round(execution_time, 2)
            }
        }), 500


@agent_bp.route('/ingest', methods=['POST'])
@jwt_required()
def agent_ingest():
    """
    Agent 入库接口
    
    请求示例：
    {
        "news_data": [
            {
                "title": "新闻标题",
                "url": "https://example.com/news/1",
                "content": "新闻正文内容..."
            }
        ],
        "source": "manual"
    }
    
    响应示例：
    {
        "code": 0,
        "data": {
            "success": true,
            "total": 1,
            "success_count": 1,
            "failed_count": 0
        },
        "message": "success"
    }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        news_data = data.get('news_data', [])
        source = data.get('source', 'api')
        
        if not news_data:
            return jsonify({
                'code': 400,
                'message': '新闻数据不能为空',
                'data': None
            }), 400
        
        agent = get_agent()
        result = agent.ingest_news(news_data)
        
        execution_time = time.time() - start_time
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                **result,
                'execution_time': round(execution_time, 2)
            }
        })
    
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Agent 入库失败: {e}")
        return jsonify({
            'code': 500,
            'message': 'Agent 入库失败',
            'data': {
                'error': str(e),
                'execution_time': round(execution_time, 2)
            }
        }), 500


@agent_bp.route('/memory', methods=['GET'])
@jwt_required()
def get_memory():
    """
    获取 Agent 记忆（对话历史）
    
    响应示例：
    {
        "code": 0,
        "data": {
            "conversation": [...],
            "user_profile": {...}
        },
        "message": "success"
    }
    """
    try:
        user_id = get_jwt_identity()
        
        agent = get_agent()
        
        conversation = agent.memory.get_conversation(user_id, limit=20)
        user_profile = agent.memory.get_user_profile(user_id)
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'conversation': conversation,
                'user_profile': user_profile
            }
        })
    
    except Exception as e:
        logger.error(f"获取记忆失败: {e}")
        return jsonify({
            'code': 500,
            'message': '获取记忆失败',
            'data': None
        }), 500


@agent_bp.route('/memory', methods=['DELETE'])
@jwt_required()
def clear_memory():
    """
    清空 Agent 记忆（对话历史）
    
    响应示例：
    {
        "code": 0,
        "message": "success",
        "data": null
    }
    """
    try:
        user_id = get_jwt_identity()
        
        agent = get_agent()
        agent.memory.clear_conversation(user_id)
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': None
        })
    
    except Exception as e:
        logger.error(f"清空记忆失败: {e}")
        return jsonify({
            'code': 500,
            'message': '清空记忆失败',
            'data': None
        }), 500


@agent_bp.route('/skills', methods=['GET'])
@jwt_required()
def list_skills():
    """
    获取已注册的 Skill 列表
    
    响应示例：
    {
        "code": 0,
        "data": {
            "skills": [
                {"name": "RetrievalSkill", "type": "skill"},
                ...
            ]
        },
        "message": "success"
    }
    """
    try:
        agent = get_agent()
        
        skills = [skill.get_info() for skill in agent.skills.values()]
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'skills': skills
            }
        })
    
    except Exception as e:
        logger.error(f"获取 Skill 列表失败: {e}")
        return jsonify({
            'code': 500,
            'message': '获取 Skill 列表失败',
            'data': None
        }), 500


@agent_bp.route('/tools', methods=['GET'])
@jwt_required()
def list_tools():
    """
    获取已注册的 Tool 列表
    
    响应示例：
    {
        "code": 0,
        "data": {
            "tools": [
                {"name": "SearchTool", "type": "tool"},
                ...
            ]
        },
        "message": "success"
    }
    """
    try:
        agent = get_agent()
        
        tools = [tool.get_info() for tool in agent.tools.values()]
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'tools': tools
            }
        })
    
    except Exception as e:
        logger.error(f"获取 Tool 列表失败: {e}")
        return jsonify({
            'code': 500,
            'message': '获取 Tool 列表失败',
            'data': None
        }), 500
