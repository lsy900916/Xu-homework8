#!/usr/bin/env python
"""
手动测试健康检查
"""
import sys
sys.path.insert(0, '..')

from core.llm import get_llm
from core.vectorstore import get_vector_store
from db.models import SessionLocal, User
from loguru import logger

logger.info("=" * 60)
logger.info("开始手动健康检查...")
logger.info("=" * 60)

# 测试 1: 数据库
logger.info("\n[1/3] 测试数据库连接...")
try:
    db = SessionLocal()
    db.query(User).first()
    db.close()
    logger.info("✓ 数据库连接成功")
except Exception as e:
    logger.error(f"✗ 数据库连接失败: {e}")

# 测试 2: FAISS
logger.info("\n[2/3] 测试 FAISS...")
try:
    vector_store = get_vector_store()
    total = vector_store.get_total_vectors()
    logger.info(f"✓ FAISS 正常 (向量数: {total})")
except Exception as e:
    logger.error(f"✗ FAISS 失败: {e}")

# 测试 3: Ollama
logger.info("\n[3/3] 测试 Ollama...")
try:
    llm = get_llm()
    logger.info(f"  配置: {llm.host} / {llm.model}")
    
    # 直接测试 HTTP 请求
    import requests
    response = requests.get(f"{llm.host}/api/version", timeout=5)
    logger.info(f"  HTTP 状态码: {response.status_code}")
    logger.info(f"  响应: {response.json()}")
    
    # 测试健康检查函数
    is_healthy = llm.check_health()
    if is_healthy:
        logger.info("✓ Ollama 健康检查通过")
    else:
        logger.error("✗ Ollama 健康检查失败")
        
except Exception as e:
    logger.error(f"✗ Ollama 测试失败: {e}")
    import traceback
    traceback.print_exc()

logger.info("\n" + "=" * 60)
logger.info("测试完成")
logger.info("=" * 60)

