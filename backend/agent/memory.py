"""
记忆模块：管理 Agent 的对话历史和用户偏好
"""
from typing import Dict, List, Optional
from loguru import logger
from datetime import datetime
import json

from db.models import SessionLocal, QueryLog, User


class BaseMemory:
    """记忆管理器基类"""
    
    def __init__(self):
        self._memory = {}
    
    def get(self, key: str):
        """获取记忆"""
        return self._memory.get(key)
    
    def set(self, key: str, value):
        """设置记忆"""
        self._memory[key] = value
    
    def get_all(self) -> Dict:
        """获取所有记忆"""
        return self._memory
    
    def clear(self):
        """清空记忆"""
        self._memory = {}


class NewsMemory(BaseMemory):
    """新闻 Agent 记忆管理器：基于数据库存储对话历史"""
    
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
    
    def get_conversation(self, user_id: int, limit: int = 10) -> List[Dict]:
        """获取用户对话历史"""
        try:
            logs = (
                self.db.query(QueryLog)
                .filter(QueryLog.user_id == user_id)
                .order_by(QueryLog.created_at.desc())
                .limit(limit)
                .all()
            )
            
            conversation = []
            for log in logs:
                conversation.append({
                    'id': log.id,
                    'query': log.query,
                    'answer': log.answer,
                    'retrieval_method': log.retrieval_method,
                    'user_feedback': log.user_feedback,
                    'created_at': log.created_at.isoformat() if log.created_at else None
                })
            
            return conversation[::-1]
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    def add_message(self, user_id: int, role: str, content: str):
        """添加消息到对话历史"""
        try:
            if role == 'user':
                log = QueryLog(
                    user_id=user_id,
                    query=content,
                    created_at=datetime.utcnow()
                )
                self.db.add(log)
                self.db.commit()
                logger.debug(f"添加用户消息: user_id={user_id}, content={content[:50]}...")
            elif role == 'assistant':
                log = (
                    self.db.query(QueryLog)
                    .filter(QueryLog.user_id == user_id)
                    .order_by(QueryLog.created_at.desc())
                    .first()
                )
                if log and not log.answer:
                    log.answer = content
                    self.db.commit()
                    logger.debug(f"添加助手回复: user_id={user_id}, answer={content[:50]}...")
        except Exception as e:
            logger.error(f"添加消息失败: {e}")
            self.db.rollback()
    
    def clear_conversation(self, user_id: int):
        """清空用户对话历史"""
        try:
            self.db.query(QueryLog).filter(QueryLog.user_id == user_id).delete()
            self.db.commit()
            logger.info(f"清空用户对话历史: user_id={user_id}")
        except Exception as e:
            logger.error(f"清空对话历史失败: {e}")
            self.db.rollback()
    
    def get_user_profile(self, user_id: int) -> Dict:
        """获取用户画像"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                return {
                    'user_id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
            return {}
        except Exception as e:
            logger.error(f"获取用户画像失败: {e}")
            return {}
    
    def update_user_profile(self, user_id: int, preferences: Dict):
        """更新用户画像"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                for key, value in preferences.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                self.db.commit()
                logger.info(f"更新用户画像: user_id={user_id}, preferences={preferences}")
        except Exception as e:
            logger.error(f"更新用户画像失败: {e}")
            self.db.rollback()
    
    def add_feedback(self, log_id: int, feedback: str, comment: str = ""):
        """添加用户反馈"""
        try:
            log = self.db.query(QueryLog).filter(QueryLog.id == log_id).first()
            if log:
                log.user_feedback = feedback
                log.feedback_comment = comment
                self.db.commit()
                logger.info(f"添加用户反馈: log_id={log_id}, feedback={feedback}")
        except Exception as e:
            logger.error(f"添加用户反馈失败: {e}")
            self.db.rollback()
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()
