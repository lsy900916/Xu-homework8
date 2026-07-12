"""
Agent 基类：定义智能代理的基本行为
"""
from typing import Dict, Any, Optional, List
from loguru import logger


class BaseAgent:
    """Agent 基类：定义智能代理的基本行为"""
    
    def __init__(self):
        self.skills: Dict[str, Any] = {}
        self.tools: Dict[str, Any] = {}
        self.memory: Optional[Any] = None
        self.planner: Optional[Any] = None
        self.name = self.__class__.__name__
    
    def register_skill(self, name: str, skill):
        """注册 Skill"""
        self.skills[name] = skill
        logger.info(f"Agent [{self.name}] 注册 Skill: {name}")
    
    def register_tool(self, name: str, tool):
        """注册 Tool"""
        self.tools[name] = tool
        logger.info(f"Agent [{self.name}] 注册 Tool: {name}")
    
    def execute(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """执行任务：规划 → 调用 Skill/Tool → 返回结果"""
        logger.info(f"Agent [{self.name}] 执行任务: {task}")
        
        if not context:
            context = {}
        
        if self.planner:
            plan = self.planner.plan(task, self)
            logger.debug(f"执行计划: {plan}")
        
        result = self._default_execute(task, context)
        
        if self.memory and context.get('user_id'):
            self.memory.add_message(context['user_id'], 'user', task)
            self.memory.add_message(context['user_id'], 'assistant', result.get('answer', ''))
        
        return result
    
    def _default_execute(self, task: str, context: Dict) -> Dict[str, Any]:
        """默认执行流程：检索 → 生成"""
        search_result = {}
        
        retrieval_skill = self.skills.get('retrieval')
        if retrieval_skill:
            search_result = retrieval_skill.search(
                query=task,
                top_k=context.get('top_k', 5)
            )
            context['search_result'] = search_result
        
        generation_skill = self.skills.get('generation')
        if generation_skill:
            answer = generation_skill.generate(
                prompt=task,
                context=context.get('search_result', {}),
                system_prompt="你是一个专业的新闻助手，基于提供的新闻内容回答用户问题。回答要准确、简洁，并引用来源。"
            )
            return {"answer": answer, **search_result}
        
        return {"answer": "未找到相关内容"}
    
    def get_memory(self) -> Dict:
        """获取记忆"""
        if self.memory:
            return self.memory.get_all()
        return {}
    
    def update_memory(self, key: str, value):
        """更新记忆"""
        if self.memory:
            self.memory.set(key, value)
    
    def use_tool(self, tool_name: str, **kwargs) -> Any:
        """使用工具"""
        tool = self.tools.get(tool_name)
        if tool:
            logger.info(f"Agent [{self.name}] 使用工具: {tool_name}")
            return tool.execute(**kwargs)
        logger.warning(f"Agent [{self.name}] 工具不存在: {tool_name}")
        return None
    
    def use_skill(self, skill_name: str, **kwargs) -> Any:
        """使用 Skill"""
        skill = self.skills.get(skill_name)
        if skill:
            logger.info(f"Agent [{self.name}] 使用 Skill: {skill_name}")
            return skill.execute(**kwargs)
        logger.warning(f"Agent [{self.name}] Skill 不存在: {skill_name}")
        return None
