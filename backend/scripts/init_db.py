#!/usr/bin/env python
"""
数据库初始化脚本
"""
from db.models import init_db
from loguru import logger

if __name__ == '__main__':
    logger.info("开始初始化数据库...")
    init_db()
    logger.info("数据库初始化完成！")

