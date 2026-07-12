"""
Tool 基类：定义工具的基本接口
"""
from typing import Dict, Any, Optional


class BaseTool:
    """Tool 基类：定义工具的基本接口"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        raise NotImplementedError
    
    def get_info(self) -> Dict[str, Any]:
        """获取工具信息"""
        return {
            'name': self.name,
            'type': 'tool'
        }
