#!/usr/bin/env python
"""
JWT 诊断脚本
"""
import sys
sys.path.insert(0, '..')

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, decode_token
from config import settings
from datetime import timedelta
import os

print("=" * 60)
print("JWT 配置诊断")
print("=" * 60)

# 显示配置
print(f"\n1. 配置信息:")
print(f"   JWT_SECRET_KEY (from settings): {settings.JWT_SECRET_KEY}")
print(f"   JWT_SECRET_KEY (from env): {os.getenv('JWT_SECRET_KEY', 'NOT SET')}")
print(f"   JWT_ALGORITHM: {settings.JWT_ALGORITHM}")

# 创建测试 app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRES)
jwt = JWTManager(app)

with app.app_context():
    # 生成测试 Token
    print(f"\n2. 生成测试 Token:")
    test_token = create_access_token(identity=1)
    print(f"   Token: {test_token[:50]}...")
    print(f"   Length: {len(test_token)}")
    
    # 解码 Token
    print(f"\n3. 解码 Token:")
    try:
        decoded = decode_token(test_token)
        print(f"   ✓ 解码成功")
        print(f"   User ID: {decoded.get('sub')}")
        print(f"   Expires: {decoded.get('exp')}")
    except Exception as e:
        print(f"   ✗ 解码失败: {e}")

print("\n" + "=" * 60)

