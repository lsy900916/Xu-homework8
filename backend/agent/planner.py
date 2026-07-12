"""
规划器模块：规划 Agent 的执行步骤
"""
from typing import List, Dict, Any, Optional
from loguru import logger


class BasePlanner:
    """规划器基类"""
    
    def plan(self, task: str, agent) -> List[Dict]:
        """规划执行步骤"""
        raise NotImplementedError
    
    def select_tool(self, task: str, available_tools: Dict) -> Optional[str]:
        """选择工具"""
        raise NotImplementedError
    
    def select_skill(self, task: str, available_skills: Dict) -> Optional[str]:
        """选择 Skill"""
        raise NotImplementedError


class NewsPlanner(BasePlanner):
    """新闻 Agent 规划器：根据任务类型规划执行步骤"""
    
    def __init__(self):
        self.task_patterns = {
            'search': ['搜索', '查找', '有哪些', '什么是', '最近'],
            'analyze': ['分析', '统计', '趋势', '聚类', '关键词'],
            'ingest': ['导入', '上传', '入库', '添加'],
            'summarize': ['总结', '摘要', '概括'],
            'qa': ['问答', '回答', '解释', '说明']
        }
    
    def plan(self, task: str, agent) -> List[Dict]:
        """规划执行步骤"""
        task_type = self._classify_task(task)
        logger.info(f"任务分类: {task_type}, 任务: {task}")
        
        if task_type == 'search' or task_type == 'qa':
            return self._plan_search(task, agent)
        elif task_type == 'analyze':
            return self._plan_analyze(task, agent)
        elif task_type == 'ingest':
            return self._plan_ingest(task, agent)
        elif task_type == 'summarize':
            return self._plan_summarize(task, agent)
        else:
            return self._plan_default(task, agent)
    
    def _classify_task(self, task: str) -> str:
        """分类任务类型"""
        task_lower = task.lower()
        for task_type, patterns in self.task_patterns.items():
            for pattern in patterns:
                if pattern in task_lower:
                    return task_type
        return 'qa'
    
    def _plan_search(self, task: str, agent) -> List[Dict]:
        """规划搜索任务"""
        plan = [
            {
                'step': 1,
                'action': 'skill',
                'name': 'retrieval',
                'method': 'search',
                'params': {'query': task, 'top_k': 5}
            },
            {
                'step': 2,
                'action': 'skill',
                'name': 'generation',
                'method': 'generate',
                'params': {'prompt': task}
            }
        ]
        
        if 'search' in agent.tools or 'fallback' in agent.tools:
            plan.insert(2, {
                'step': 2,
                'action': 'tool',
                'name': 'search',
                'method': 'search_baidu',
                'params': {'query': task, 'num_results': 3}
            })
        
        return plan
    
    def _plan_analyze(self, task: str, agent) -> List[Dict]:
        """规划分析任务"""
        plan = [
            {
                'step': 1,
                'action': 'skill',
                'name': 'analysis',
                'method': 'cluster_analysis',
                'params': {'time_range': 'weekly'}
            }
        ]
        
        if 'keywords' in task.lower():
            plan.append({
                'step': 2,
                'action': 'skill',
                'name': 'analysis',
                'method': 'keyword_statistics',
                'params': {'time_range': 'weekly', 'top_n': 10}
            })
        
        return plan
    
    def _plan_ingest(self, task: str, agent) -> List[Dict]:
        """规划入库任务"""
        return [
            {
                'step': 1,
                'action': 'skill',
                'name': 'ingestion',
                'method': 'batch_ingest',
                'params': {}
            }
        ]
    
    def _plan_summarize(self, task: str, agent) -> List[Dict]:
        """规划总结任务"""
        return [
            {
                'step': 1,
                'action': 'skill',
                'name': 'retrieval',
                'method': 'search',
                'params': {'query': task, 'top_k': 5}
            },
            {
                'step': 2,
                'action': 'skill',
                'name': 'generation',
                'method': 'summarize',
                'params': {'prompt': task}
            }
        ]
    
    def _plan_default(self, task: str, agent) -> List[Dict]:
        """默认规划"""
        return [
            {
                'step': 1,
                'action': 'skill',
                'name': 'retrieval',
                'method': 'search',
                'params': {'query': task, 'top_k': 5}
            },
            {
                'step': 2,
                'action': 'skill',
                'name': 'generation',
                'method': 'generate',
                'params': {'prompt': task}
            }
        ]
    
    def select_tool(self, task: str, available_tools: Dict) -> Optional[str]:
        """选择工具"""
        task_lower = task.lower()
        
        tool_mapping = {
            '搜索': 'search',
            '爬虫': 'crawler',
            '数据库': 'database',
            '邮件': 'email'
        }
        
        for pattern, tool_name in tool_mapping.items():
            if pattern in task_lower and tool_name in available_tools:
                return tool_name
        
        return None
    
    def select_skill(self, task: str, available_skills: Dict) -> Optional[str]:
        """选择 Skill"""
        task_lower = task.lower()
        
        skill_mapping = {
            '搜索': 'retrieval',
            '查找': 'retrieval',
            '回答': 'generation',
            '生成': 'generation',
            '分析': 'analysis',
            '统计': 'analysis',
            '导入': 'ingestion',
            '入库': 'ingestion'
        }
        
        for pattern, skill_name in skill_mapping.items():
            if pattern in task_lower and skill_name in available_skills:
                return skill_name
        
        return None
    
    def execute_plan(self, plan: List[Dict], agent, context: Optional[Dict] = None) -> Dict[str, Any]:
        """执行规划"""
        results = {}
        
        for step in plan:
            action = step['action']
            name = step['name']
            method = step['method']
            params = step.get('params', {})
            
            if context:
                params.update(context)
            
            try:
                if action == 'skill':
                    skill = agent.skills.get(name)
                    if skill and hasattr(skill, method):
                        result = getattr(skill, method)(**params)
                        results[f'step_{step["step"]}'] = result
                elif action == 'tool':
                    tool = agent.tools.get(name)
                    if tool and hasattr(tool, method):
                        result = getattr(tool, method)(**params)
                        results[f'step_{step["step"]}'] = result
            except Exception as e:
                logger.error(f"执行步骤 {step['step']} 失败: {e}")
        
        return results
