"""
健康检查 API
"""
from flask import Blueprint, jsonify
from datetime import datetime
from loguru import logger

from core.vectorstore import get_vector_store
from core.llm import get_llm
from db.models import SessionLocal, User
from config import settings

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查
    
    响应:
    {
        "status": "healthy",
        "timestamp": "2026-6-30T10:30:00Z",
        "services": {
            "database": {"status": "up"},
            "faiss": {"status": "up", "total_vectors": 1000},
            "ollama": {"status": "up", "model": "qwen2.5:3b"}
        }
    }
    """
    services = {}
    overall_status = "healthy"
    
    # 检查数据库
    try:
        db = SessionLocal()
        db.query(User).first()
        db.close()
        services['database'] = {'status': 'up'}
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        services['database'] = {'status': 'down', 'error': str(e)}
        overall_status = "unhealthy"
    
    # 检查 FAISS
    try:
        vector_store = get_vector_store()
        services['faiss'] = {
            'status': 'up',
            'total_vectors': vector_store.get_total_vectors()
        }
    except Exception as e:
        logger.error(f"FAISS 健康检查失败: {e}")
        services['faiss'] = {'status': 'down', 'error': str(e)}
        overall_status = "unhealthy"
    
    # 检查 Ollama（使用统一 LLM 客户端的健康检查，以真实可用性为准）
    try:
        llm = get_llm()
        if llm.check_health():
            services['ollama'] = {
                'status': 'up',
                'model': settings.OLLAMA_MODEL,
                'host': llm.host
            }
        else:
            services['ollama'] = {'status': 'down'}
            overall_status = "degraded"
    except Exception as e:
        logger.error(f"Ollama 健康检查失败: {e}")
        services['ollama'] = {'status': 'down', 'error': str(e)}
        overall_status = "degraded"
    
    # 仅当关键依赖（数据库/FAISS）不可用时返回 503；
    # 如果只是 LLM 等非关键服务不可用（degraded），返回 200 并在 body 中标示状态
    status_code = 200 if overall_status in ("healthy", "degraded") else 503
    
    return jsonify({
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'services': services,
        'version': settings.APP_VERSION
    }), status_code

