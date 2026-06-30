#!/usr/bin/env python
"""
创建管理员账户脚本
"""
from db.models import SessionLocal
from db.dao import UserDAO
from passlib.hash import bcrypt
from loguru import logger
import sys

def create_admin(email: str, password: str, username: str = "Admin"):
    """创建管理员账户"""
    db = SessionLocal()
    
    try:
        # 检查是否已存在
        existing = UserDAO.get_by_email(db, email)
        if existing:
            logger.warning(f"管理员账户已存在: {email}")
            return
        
        # 创建管理员
        password_hash = bcrypt.hash(password, rounds=12)
        user = UserDAO.create(db, email, password_hash, username)
        
        # 设置为管理员
        user.role = 'admin'
        db.commit()
        
        logger.info(f"管理员账户创建成功: {email}")
        print(f"\n✓ 管理员账户创建成功！")
        print(f"  邮箱: {email}")
        print(f"  用户名: {username}")
        print(f"  密码: {password}")
        print(f"\n请妥善保管管理员密码！\n")
    
    except Exception as e:
        logger.error(f"创建管理员失败: {e}")
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='创建管理员账户')
    parser.add_argument('--email', type=str, default='admin@xu-news.com', help='管理员邮箱')
    parser.add_argument('--password', type=str, default='Admin123', help='管理员密码')
    parser.add_argument('--username', type=str, default='Admin', help='管理员用户名')
    
    args = parser.parse_args()
    
    create_admin(args.email, args.password, args.username)

