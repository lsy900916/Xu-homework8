"""
数据库工具：封装数据库操作
"""
from typing import List, Dict, Any, Optional
from loguru import logger
from sqlalchemy import text

from db.models import SessionLocal
from .base_tool import BaseTool


class DatabaseTool(BaseTool):
    """数据库工具：封装数据库操作"""
    
    def __init__(self):
        super().__init__()
    
    def query(self, sql: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        查询数据
        
        Args:
            sql: SQL 语句
            params: 参数字典
        
        Returns:
            查询结果
        """
        logger.info(f"数据库工具执行查询: {sql[:50]}...")
        
        db = SessionLocal()
        try:
            if params:
                result = db.execute(text(sql), params)
            else:
                result = db.execute(text(sql))
            
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result]
        
        except Exception as e:
            logger.error(f"数据库查询失败: {e}")
            return []
        
        finally:
            db.close()
    
    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        插入数据
        
        Args:
            table: 表名
            data: 数据字典
        
        Returns:
            插入结果
        """
        logger.info(f"数据库工具执行插入: table={table}, keys={list(data.keys())}")
        
        db = SessionLocal()
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join([f":{k}" for k in data.keys()])
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            db.execute(text(sql), data)
            db.commit()
            
            return {"success": True, "rows_affected": 1}
        
        except Exception as e:
            logger.error(f"数据库插入失败: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
        
        finally:
            db.close()
    
    def update(self, table: str, data: Dict[str, Any], where: str) -> Dict[str, Any]:
        """
        更新数据
        
        Args:
            table: 表名
            data: 数据字典
            where: WHERE 条件
        
        Returns:
            更新结果
        """
        logger.info(f"数据库工具执行更新: table={table}, where={where}")
        
        db = SessionLocal()
        try:
            set_clause = ', '.join([f"{k} = :{k}" for k in data.keys()])
            sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
            
            result = db.execute(text(sql), data)
            db.commit()
            
            return {"success": True, "rows_affected": result.rowcount}
        
        except Exception as e:
            logger.error(f"数据库更新失败: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
        
        finally:
            db.close()
    
    def delete(self, table: str, where: str) -> Dict[str, Any]:
        """
        删除数据
        
        Args:
            table: 表名
            where: WHERE 条件
        
        Returns:
            删除结果
        """
        logger.info(f"数据库工具执行删除: table={table}, where={where}")
        
        db = SessionLocal()
        try:
            sql = f"DELETE FROM {table} WHERE {where}"
            
            result = db.execute(text(sql))
            db.commit()
            
            return {"success": True, "rows_affected": result.rowcount}
        
        except Exception as e:
            logger.error(f"数据库删除失败: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
        
        finally:
            db.close()
    
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        action = kwargs.get('action', 'query')
        
        if action == 'query':
            return self.query(
                sql=kwargs['sql'],
                params=kwargs.get('params')
            )
        elif action == 'insert':
            return self.insert(
                table=kwargs['table'],
                data=kwargs['data']
            )
        elif action == 'update':
            return self.update(
                table=kwargs['table'],
                data=kwargs['data'],
                where=kwargs['where']
            )
        elif action == 'delete':
            return self.delete(
                table=kwargs['table'],
                where=kwargs['where']
            )
        
        return {"error": f"不支持的操作: {action}"}
