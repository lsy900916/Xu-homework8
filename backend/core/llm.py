"""
Ollama LLM 接入：qwen2.5:3b
"""
import requests
from typing import Optional, Dict, Any
from loguru import logger
import time

from config import settings


class OllamaLLM:
    """Ollama LLM 封装"""
    
    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.temperature = settings.OLLAMA_TEMPERATURE
        self.max_tokens = settings.OLLAMA_MAX_TOKENS
        self.api_url = f"{self.host}/api/generate"

    def _normalize_host(self, host: str) -> str:
        """
        规范 OLLAMA_HOST：
        - scheme 小写
        - localhost/::1/0.0.0.0 统一为 127.0.0.1（0.0.0.0 是监听地址，不能用于请求）
        - 移除末尾斜杠
        """
        try:
            h = (host or '').strip()
            h = h.replace('HTTP://', 'http://').replace('HTTPS://', 'https://')
            h = h.replace('localhost', '127.0.0.1').replace('::1', '127.0.0.1').replace('0.0.0.0', '127.0.0.1')
            if h.endswith('/'):
                h = h[:-1]
            return h
        except Exception:
            return host

    def _sync_from_settings(self):
        """在每次调用前同步最新配置，避免单例在启动后主机变更仍使用旧地址。"""
        current = self._normalize_host(settings.OLLAMA_HOST)
        # 无条件写回规范化后的主机，避免 self.host 保留未规范化的值（例如 0.0.0.0）
        if self.host != current:
            logger.info(f"Ollama 主机同步为: {current}")
        self.host = current
        self.api_url = f"{self.host}/api/generate"
    
    def generate(
        self, 
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成文本
        
        Args:
            prompt: 用户输入
            temperature: 温度参数（可选）
            max_tokens: 最大 token 数（可选）
            system_prompt: 系统提示词（可选）
            
        Returns:
            {
                "text": "生成的文本",
                "response_time": 3.2,
                "tokens": 150
            }
        """
        temperature = temperature or self.temperature
        max_tokens = max_tokens or self.max_tokens
        
        # 构建完整 prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        # 每次调用前同步主机配置
        self._sync_from_settings()

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            logger.debug(f"调用 Ollama LLM，模型: {self.model}, Prompt 长度: {len(full_prompt)}")
            
            start_time = time.time()
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            response_time = time.time() - start_time
            
            result = response.json()
            
            generated_text = result.get('response', '')
            
            logger.info(f"LLM 生成成功，耗时: {response_time:.2f}s, 输出长度: {len(generated_text)}")
            
            return {
                "text": generated_text,
                "response_time": response_time,
                "tokens": len(generated_text.split())  # 简单估算
            }
        
        except requests.exceptions.Timeout:
            logger.error(f"Ollama LLM 请求超时（> {self.timeout}s）")
            raise Exception("LLM 请求超时")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama LLM 请求失败: {e}")
            raise Exception(f"LLM 请求失败: {str(e)}")
        
        except Exception as e:
            logger.error(f"LLM 生成失败: {e}")
            raise
    
    def check_health(self) -> bool:
        """检查 Ollama 服务是否可用"""
        try:
            # 每次调用前同步主机配置
            self._sync_from_settings()
            logger.debug(f"检查 Ollama 健康状态: {self.host}/api/version")
            response = requests.get(f"{self.host}/api/version", timeout=5)
            logger.debug(f"Ollama 响应状态码: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama 健康检查失败: {e}")
            return False


# 单例模式
_llm = None


def get_llm() -> OllamaLLM:
    """获取 LLM 单例"""
    global _llm
    if _llm is None:
        _llm = OllamaLLM()
    return _llm

