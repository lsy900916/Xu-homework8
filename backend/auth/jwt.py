"""
JWT 认证：登录、注册、令牌校验、密码散列
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt as bcrypt_lib
from datetime import datetime, timedelta
from loguru import logger
import re

from db.models import SessionLocal
from db.dao import UserDAO
from config import settings

auth_bp = Blueprint('auth', __name__)


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """
    验证密码强度
    - 长度 8-32 位
    - 包含字母和数字
    """
    if len(password) < 8 or len(password) > 32:
        return False
    
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_letter and has_digit


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    
    请求体:
    {
        "email": "user@example.com",
        "password": "Password123",
        "username": "User1"
    }
    
    响应:
    {
        "code": 0,
        "message": "注册成功",
        "data": {
            "user_id": 123,
            "email": "user@example.com",
            "username": "User1"
        }
    }
    """
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        username = data.get('username', email.split('@')[0])
        
        # 参数验证
        if not email or not password:
            return jsonify({
                'code': 40000,
                'message': '邮箱和密码不能为空',
                'data': None
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'code': 40000,
                'message': '邮箱格式错误',
                'data': None
            }), 400
        
        if not validate_password(password):
            return jsonify({
                'code': 40000,
                'message': '密码强度不足（8-32位，包含字母和数字）',
                'data': None
            }), 400
        
        db = SessionLocal()
        try:
            # 检查邮箱是否已存在
            existing_user = UserDAO.get_by_email(db, email)
            if existing_user:
                return jsonify({
                    'code': 40009,
                    'message': '邮箱已被注册',
                    'data': None
                }), 409
            
            # 密码加密
            password_hash = bcrypt_lib.hashpw(
                password.encode('utf-8'), 
                bcrypt_lib.gensalt(rounds=settings.BCRYPT_ROUNDS)
            ).decode('utf-8')
            
            # 创建用户
            user = UserDAO.create(db, email, password_hash, username)
            
            logger.info(f"用户注册成功: {email}")
            
            return jsonify({
                'code': 0,
                'message': '注册成功',
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'created_at': user.created_at.isoformat()
                }
            }), 200
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"注册失败: {e}")
        return jsonify({
            'code': 50000,
            'message': f'注册失败: {str(e)}',
            'data': None
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    
    请求体:
    {
        "email": "user@example.com",
        "password": "Password123"
    }
    
    响应:
    {
        "code": 0,
        "message": "登录成功",
        "data": {
            "token": "eyJhbGci...",
            "expires_in": 86400,
            "user": {
                "user_id": 123,
                "email": "user@example.com",
                "username": "User1"
            }
        }
    }
    """
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'code': 40000,
                'message': '邮箱和密码不能为空',
                'data': None
            }), 400
        
        db = SessionLocal()
        try:
            # 查询用户
            user = UserDAO.get_by_email(db, email)
            
            if not user:
                return jsonify({
                    'code': 40001,
                    'message': '邮箱或密码错误',
                    'data': None
                }), 401
            
            # 检查账户是否锁定
            if user.is_locked:
                if user.locked_until and datetime.utcnow() < user.locked_until:
                    return jsonify({
                        'code': 40003,
                        'message': f'账户已锁定，请于 {user.locked_until.isoformat()} 后重试',
                        'data': {
                            'locked_until': user.locked_until.isoformat()
                        }
                    }), 403
                else:
                    # 锁定已过期，重置
                    UserDAO.reset_failed_login(db, user)
            
            # 验证密码
            if not bcrypt_lib.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                # 登录失败
                UserDAO.increment_failed_login(db, user)
                
                remaining = max(0, 5 - user.failed_login_attempts)
                
                return jsonify({
                    'code': 40001,
                    'message': '邮箱或密码错误',
                    'data': {
                        'remaining_attempts': remaining
                    }
                }), 401
            
            # 登录成功，重置失败次数
            UserDAO.reset_failed_login(db, user)
            
            


            from flask import current_app
            logger.info(f"当前 JWT_SECRET_KEY: {current_app.config.get('JWT_SECRET_KEY')}")




            # 生成 JWT Token（注意：PyJWT 2.x 要求 sub 为字符串）
            token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRES)
            )
            
            logger.info(f"用户登录成功: {email}")
            
            return jsonify({
                'code': 0,
                'message': '登录成功',
                'data': {
                    'token': token,
                    'expires_in': settings.JWT_ACCESS_TOKEN_EXPIRES,
                    'user': {
                        'user_id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'role': user.role
                    }
                }
            }), 200
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({
            'code': 50000,
            'message': f'登录失败: {str(e)}',
            'data': None
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    获取当前用户信息
    
    响应:
    {
        "code": 0,
        "data": {
            "user_id": 123,
            "email": "user@example.com",
            "username": "User1",
            "role": "user"
        }
    }
    """
    from flask import request, current_app
    logger.info(f"收到请求头: {dict(request.headers)}")
    logger.info(f"JWT配置: {current_app.config['JWT_SECRET_KEY'][:10]}...")

    try:
        # 获取并记录 Token
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            logger.info(f"收到Token: {token[:50]}...")
        
        user_id = get_jwt_identity()
        logger.info(f"解析出用户ID: {user_id}")
        # 兼容字符串/数字形式的用户ID
        try:
            user_id = int(user_id)
        except Exception:
            pass
        
        db = SessionLocal()
        try:
            user = UserDAO.get_by_id(db, user_id)
            
            if not user:
                return jsonify({
                    'code': 40004,
                    'message': '用户不存在',
                    'data': None
                }), 404
            
            return jsonify({
                'code': 0,
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role,
                    'created_at': user.created_at.isoformat()
                }
            }), 200
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return jsonify({
            'code': 50000,
            'message': f'获取用户信息失败: {str(e)}',
            'data': None
        }), 500

