"""
Flask 应用入口
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from loguru import logger
from datetime import timedelta
import sys

from config import settings
from db.models import init_db

# 导入 API 蓝图
from apis.health import health_bp
from apis.ingest import ingest_bp
from apis.search import search_bp
from apis.reports import reports_bp
from apis.agent_api import agent_bp
from auth.jwt import auth_bp


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__)
    
    # ==================== 配置加载 ====================
    app.config['SECRET_KEY'] = settings.JWT_SECRET_KEY
    app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRES)
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'
    app.config['JSON_AS_ASCII'] = False  # 支持中文 JSON
    
    # ==================== 日志配置 ====================
    logger.remove()
    logger.add(
        sys.stdout,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        colorize=True
    )
    logger.add(
        settings.LOG_DIR / "app.log",
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="30 days",
        compression="gz"
    )
    
    # ==================== CORS ====================
    CORS(app, origins=settings.CORS_ORIGINS, supports_credentials=True)
    
    # ==================== JWT ====================
    jwt = JWTManager(app)
    
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({
            'code': 40001,
            'message': '缺少认证令牌',
            'data': None
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({
            'code': 40001,
            'message': '无效的令牌',
            'data': None
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'code': 40001,
            'message': '令牌已过期',
            'data': None
        }), 401
    
    # ==================== 初始化数据库 ====================
    with app.app_context():
        init_db()
        logger.info("数据库初始化完成")
    
    # ==================== 注册蓝图 ====================
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(ingest_bp, url_prefix='/api/ingest')
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api/report')
    app.register_blueprint(agent_bp, url_prefix='/api/agent')
    
    # ==================== 全局错误处理 ====================
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 40004,
            'message': '资源不存在',
            'data': None
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"服务器内部错误: {error}")
        return jsonify({
            'code': 50000,
            'message': '服务器内部错误',
            'data': None
        }), 500
    
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动成功")
    logger.info(f"环境: {settings.APP_ENV}")
    logger.info(f"Ollama 地址: {settings.OLLAMA_HOST}")
    logger.info(f"Embedding 模型: {settings.EMBEDDING_MODEL}")
    logger.info(f"JWT_SECRET_KEY 已加载: {app.config['JWT_SECRET_KEY']}")

    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG
    )

