"""
生成 Skill：封装 LLM 生成、摘要和关键词提取功能
"""
from typing import List, Dict, Any, Optional
from loguru import logger

from core.llm import get_llm
from .base_skill import BaseSkill


class GenerationSkill(BaseSkill):
    """生成 Skill：封装 LLM 生成、摘要和关键词提取功能"""
    
    def __init__(self):
        super().__init__()
        self.llm = get_llm()
    
    def generate(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        生成答案
        
        Args:
            prompt: 用户输入
            context: 上下文信息
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大 token 数
        
        Returns:
            生成文本
        """
        logger.info(f"生成 Skill 执行生成: prompt 长度={len(prompt)}")
        
        # 构建完整上下文
        if context and context.get('sources'):
            context_text = self._build_context(context['sources'])
            full_prompt = f"""请基于以下新闻内容回答用户的问题。

新闻内容：
{context_text}

用户问题：{prompt}

请提供准确、简洁的答案，并在答案中标注来源（如"根据来源1..."）。如果新闻内容无法回答问题，请明确说明。

答案："""
        else:
            full_prompt = prompt
        
        default_system_prompt = "你是一个专业的新闻助手，基于提供的新闻内容回答用户问题。回答要准确、简洁，并引用来源。"
        system_prompt = system_prompt or default_system_prompt
        
        try:
            result = self.llm.generate(
                prompt=full_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return result.get('text', '')
        
        except Exception as e:
            logger.error(f"LLM 生成失败: {e}")
            if context and context.get('sources'):
                preview = "\n\n".join([
                    f"- {c.get('article_title') or '未知标题'}: {c['text'][:120]}"
                    for c in context['sources'][:5]
                ])
                return f"当前生成模型不可用，已提供基于检索内容的要点摘要：\n{preview}"
            return "生成失败，请稍后重试。"
    
    def summarize(self, text: str, max_length: int = 200) -> str:
        """
        文本摘要
        
        Args:
            text: 输入文本
            max_length: 摘要最大长度
        
        Returns:
            摘要文本
        """
        logger.info(f"生成 Skill 执行摘要: 文本长度={len(text)}")
        
        prompt = f"""请对以下文本进行摘要，保持核心信息，控制在 {max_length} 字以内：

文本：
{text}

摘要："""
        
        try:
            result = self.llm.generate(
                prompt=prompt,
                system_prompt="你是一个专业的文本摘要助手，能够准确提取核心信息。"
            )
            return result.get('text', '')[:max_length]
        
        except Exception as e:
            logger.error(f"摘要生成失败: {e}")
            return text[:max_length]
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """
        关键词提取
        
        Args:
            text: 输入文本
            top_n: 返回关键词数量
        
        Returns:
            关键词列表
        """
        logger.info(f"生成 Skill 执行关键词提取: 文本长度={len(text)}")
        
        prompt = f"""请从以下文本中提取 {top_n} 个最核心的关键词，用逗号分隔：

文本：
{text}

关键词："""
        
        try:
            result = self.llm.generate(
                prompt=prompt,
                system_prompt="你是一个专业的关键词提取助手，能够准确识别文本中的核心概念。"
            )
            keywords = result.get('text', '')
            return [k.strip() for k in keywords.split(',')[:top_n]]
        
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return []
    
    def _build_context(self, sources: List[Dict]) -> str:
        """构建上下文文本"""
        context_parts = []
        for i, source in enumerate(sources, 1):
            title = source.get('article_title', '未知')
            text = source.get('text', '')
            context_parts.append(f"[来源 {i}] {title}\n{text}")
        
        return "\n\n".join(context_parts)
    
    def execute(self, **kwargs) -> Any:
        """执行技能"""
        action = kwargs.get('action', 'generate')
        
        if action == 'generate':
            return self.generate(
                prompt=kwargs['prompt'],
                context=kwargs.get('context'),
                system_prompt=kwargs.get('system_prompt'),
                temperature=kwargs.get('temperature'),
                max_tokens=kwargs.get('max_tokens')
            )
        elif action == 'summarize':
            return self.summarize(
                text=kwargs['text'],
                max_length=kwargs.get('max_length', 200)
            )
        elif action == 'extract_keywords':
            return self.extract_keywords(
                text=kwargs['text'],
                top_n=kwargs.get('top_n', 5)
            )
        
        return {"error": f"不支持的操作: {action}"}
