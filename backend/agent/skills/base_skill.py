"""
Skill 基类：定义技能的基本接口
"""
from typing import Dict, Any, Optional


class BaseSkill:
    """Skill 基类：定义技能的基本接口"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    def execute(self, **kwargs) -> Any:
        """执行技能"""
        raise NotImplementedError
    
    def get_info(self) -> Dict[str, Any]:
        """获取技能信息"""
        return {
            'name': self.name,
            'type': 'skill'
        }
