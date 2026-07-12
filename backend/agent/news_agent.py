"""
NewsAgent 实现类：新闻智能代理
"""
from typing import Dict, Any, Optional
from loguru import logger

from .base_agent import BaseAgent
from .skills.retrieval_skill import RetrievalSkill
from .skills.generation_skill import GenerationSkill
from .skills.analysis_skill import AnalysisSkill
from .skills.ingestion_skill import IngestionSkill
from .tools.search_tool import SearchTool
from .tools.crawler_tool import CrawlerTool
from .tools.database_tool import DatabaseTool
from .tools.email_tool import EmailTool
from .memory import NewsMemory
from .planner import NewsPlanner


class NewsAgent(BaseAgent):
    """新闻智能代理：封装 RAG 检索、生成、分析能力"""
    
    def __init__(self):
        super().__init__()
        self.name = "NewsAgent"
        
        # 注册核心 Skill
        self.register_skill('retrieval', RetrievalSkill())
        self.register_skill('generation', GenerationSkill())
        self.register_skill('analysis', AnalysisSkill())
        self.register_skill('ingestion', IngestionSkill())
        
        # 注册工具
        self.register_tool('search', SearchTool())
        self.register_tool('crawler', CrawlerTool())
        self.register_tool('database', DatabaseTool())
        self.register_tool('email', EmailTool())
        
        # 初始化记忆和规划器
        self.memory = NewsMemory()
        self.planner = NewsPlanner()
    
    def answer_question(self, question: str, user_id: Optional[int] = None, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        回答用户问题（核心 RAG 流程）
        
        Args:
            question: 用户问题
            user_id: 用户 ID
            options: 查询选项（top_k, enable_fallback）
        
        Returns:
            回答结果
        """
        logger.info(f"NewsAgent 回答问题: user_id={user_id}, question='{question[:50]}...'")
        
        if options is None:
            options = {}
        
        context = {
            'user_id': user_id,
            'top_k': options.get('top_k', 5),
            'enable_fallback': options.get('enable_fallback', True)
        }
        
        # 获取对话历史
        if user_id and self.memory:
            context['conversation_history'] = self.memory.get_conversation(user_id, limit=5)
        
        return self._execute_rag(question, context)
    
    def _execute_rag(self, question: str, context: Dict) -> Dict[str, Any]:
        """
        执行 RAG 流程
        
        Args:
            question: 用户问题
            context: 上下文
        
        Returns:
            RAG 执行结果
        """
        # 1. 规划
        plan = self.planner.plan(question, self)
        logger.debug(f"执行计划: {plan}")
        
        # 2. 执行检索
        retrieval_skill = self.skills.get('retrieval')
        search_result = retrieval_skill.search(
            query=question,
            top_k=context.get('top_k', 5)
        )
        context['search_result'] = search_result
        
        # 3. 检查是否需要回退搜索
        sources = search_result.get('sources', [])
        if not sources and context.get('enable_fallback'):
            logger.info("知识库检索为空，触发回退搜索")
            search_tool = self.tools.get('search')
            fallback_results = search_tool.search_baidu(question, num_results=3)
            
            # 将搜索结果添加到上下文
            context['fallback_results'] = fallback_results
            context['search_result']['sources'] = [
                {
                    'chunk_id': f'fallback_{i}',
                    'text': r.get('snippet', ''),
                    'article_title': r.get('title', ''),
                    'article_url': r.get('url', ''),
                    'retrieval_score': 0.5
                }
                for i, r in enumerate(fallback_results)
            ]
        
        # 4. 生成答案
        generation_skill = self.skills.get('generation')
        answer = generation_skill.generate(
            prompt=question,
            context=context.get('search_result', {}),
            system_prompt="你是一个专业的新闻助手，基于提供的新闻内容回答用户问题。回答要准确、简洁，并引用来源。"
        )
        
        # 5. 更新记忆
        if self.memory and context.get('user_id'):
            self.memory.add_message(context['user_id'], 'user', question)
            self.memory.add_message(context['user_id'], 'assistant', answer)
        
        return {
            "answer": answer,
            "sources": context['search_result'].get('sources', []),
            "retrieval_stats": context['search_result'].get('retrieval_stats', {}),
            "plan": [p['name'] for p in plan],
            "memory_updated": True
        }
    
    def analyze_clusters(self, time_range: str = 'weekly') -> Dict[str, Any]:
        """
        执行聚类分析
        
        Args:
            time_range: 时间范围
        
        Returns:
            聚类分析结果
        """
        logger.info(f"NewsAgent 执行聚类分析: time_range={time_range}")
        
        analysis_skill = self.skills.get('analysis')
        if analysis_skill:
            return analysis_skill.cluster_analysis(time_range=time_range)
        
        return {"error": "分析 Skill 未注册"}
    
    def analyze_keywords(self, time_range: str = 'weekly', top_n: int = 10) -> Dict[str, Any]:
        """
        关键词统计分析
        
        Args:
            time_range: 时间范围
            top_n: 返回数量
        
        Returns:
            关键词统计结果
        """
        logger.info(f"NewsAgent 执行关键词统计: time_range={time_range}, top_n={top_n}")
        
        analysis_skill = self.skills.get('analysis')
        if analysis_skill:
            return analysis_skill.keyword_statistics(time_range=time_range, top_n=top_n)
        
        return {"error": "分析 Skill 未注册"}
    
    def ingest_news(self, news_data: list) -> Dict[str, Any]:
        """
        入库新闻数据
        
        Args:
            news_data: 新闻数据列表
        
        Returns:
            入库结果
        """
        logger.info(f"NewsAgent 入库新闻数据: 数量={len(news_data)}")
        
        ingestion_skill = self.skills.get('ingestion')
        if ingestion_skill:
            return ingestion_skill.batch_ingest(news_data)
        
        return {"error": "入库 Skill 未注册"}
    
    def execute(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            task: 任务描述
            context: 上下文
        
        Returns:
            执行结果
        """
        logger.info(f"NewsAgent 执行任务: '{task[:50]}...'")
        
        if not context:
            context = {}
        
        # 规划
        plan = self.planner.plan(task, self)
        
        # 执行规划
        results = self.planner.execute_plan(plan, self, context)
        
        # 更新记忆
        if self.memory and context.get('user_id'):
            self.memory.add_message(context['user_id'], 'user', task)
            answer = results.get('step_2') or results.get('step_1') or ''
            if isinstance(answer, dict):
                answer = str(answer)
            self.memory.add_message(context['user_id'], 'assistant', answer[:500])
        
        return {
            "results": results,
            "plan": [p['name'] for p in plan],
            "memory_updated": True
        }
