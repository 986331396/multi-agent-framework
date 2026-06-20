"""
LLM 客户端模块
统一封装多 Provider（OpenAI / DeepSeek / Qwen / CodeBuddy）的 LLM 调用
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class LLMClient:
    """
    统一 LLM 客户端

    支持的 Provider:
      - openai:    https://api.openai.com/v1
      - deepseek:  https://api.deepseek.com/v1
      - qwen:      https://dashscope.aliyuncs.com/compatible-mode/v1
      - codebuddy: https://api.codebuddy.cn/v1

    所有 Provider 都兼容 OpenAI Chat Completions API 格式，
    只是 base_url 和 api_key 不同。
    """

    def __init__(self, llm_providers_config: Dict[str, Any]):
        self.providers: Dict[str, Dict] = {}
        self._init_providers(llm_providers_config)

    def _init_providers(self, config: Dict[str, Any]):
        """初始化所有 Provider 配置"""
        for provider_name, provider_config in config.items():
            api_key = self._resolve_env(provider_config.get("api_key", ""))
            self.providers[provider_name] = {
                "provider": provider_config.get("provider", provider_name),
                "base_url": provider_config.get("base_url", ""),
                "api_key": api_key,
                "models": provider_config.get("models", {}),
            }
            status = "OK" if api_key else "NO_KEY"
            logger.info(
                f"LLM Provider 注册: {provider_name} "
                f"({provider_config.get('base_url', '')}) [{status}]"
            )

    @staticmethod
    def _resolve_env(value: str) -> str:
        """解析 ${ENV_VAR} 格式的环境变量"""
        import re
        pattern = r'\$\{(\w+)\}'
        def replace_var(m):
            return os.environ.get(m.group(1), "")
        return re.sub(pattern, replace_var, value)

    def get_provider_config(self, provider_name: str) -> Optional[Dict]:
        """获取指定 Provider 的配置"""
        return self.providers.get(provider_name)

    def get_model_config(self, provider_name: str, model_name: str) -> Dict:
        """获取指定模型的参数配置"""
        provider = self.providers.get(provider_name, {})
        models = provider.get("models", {})
        return models.get(model_name, {"max_tokens": 4096, "temperature": 0.7})

    async def chat(
        self,
        provider_name: str,
        model_name: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用 LLM Chat Completion

        Args:
            provider_name: Provider 名称 (openai/deepseek/qwen/codebuddy)
            model_name: 模型名称 (gpt-4o/deepseek-chat/...)
            messages: 消息列表 [{"role": "system/user/assistant", "content": "..."}]
            **kwargs: 额外参数 (max_tokens, temperature 等)

        Returns:
            {"content": "回复内容", "model": "模型名", "usage": {...}}
        """
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"未知的 LLM Provider: {provider_name}")

        if not provider["api_key"]:
            logger.warning(
                f"Provider '{provider_name}' 缺少 API Key，"
                f"返回模拟响应"
            )
            return self._mock_response(provider_name, model_name, messages)

        # 合并模型默认参数与传入参数
        model_config = self.get_model_config(provider_name, model_name)
        request_body = {
            "model": model_name,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", model_config.get("max_tokens", 4096)),
            "temperature": kwargs.get("temperature", model_config.get("temperature", 0.7)),
        }

        url = f"{provider['base_url']}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {provider['api_key']}",
        }

        logger.debug(
            f"LLM 调用: provider={provider_name}, model={model_name}, "
            f"messages={len(messages)}条"
        )

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=request_body, headers=headers)
                response.raise_for_status()
                data = response.json()

                return {
                    "content": data["choices"][0]["message"]["content"],
                    "model": data.get("model", model_name),
                    "usage": data.get("usage", {}),
                    "provider": provider_name,
                }
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM 调用失败 (HTTP {e.response.status_code}): {e}")
            return self._error_response(provider_name, model_name, str(e))
        except Exception as e:
            logger.error(f"LLM 调用异常: {e}")
            return self._error_response(provider_name, model_name, str(e))

    async def chat_with_system(
        self,
        provider_name: str,
        model_name: str,
        system_prompt: str,
        user_message: str,
        **kwargs
    ) -> Dict[str, Any]:
        """带系统提示词的便捷调用"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        return await self.chat(provider_name, model_name, messages, **kwargs)

    def _mock_response(
        self, provider: str, model: str, messages: List[Dict]
    ) -> Dict[str, Any]:
        """无 API Key 时的模拟响应（用于测试）"""
        last_msg = messages[-1]["content"][:100] if messages else ""
        return {
            "content": (
                f"[模拟响应 - {provider}/{model}]\n"
                f"已收到请求: {last_msg}...\n"
                f"请配置 API Key 以启用真实 LLM 调用。"
            ),
            "model": model,
            "provider": provider,
            "usage": {"total_tokens": 0},
            "mock": True,
        }

    def _error_response(
        self, provider: str, model: str, error: str
    ) -> Dict[str, Any]:
        """错误响应"""
        return {
            "content": f"[LLM 调用失败] {error}",
            "model": model,
            "provider": provider,
            "error": error,
        }

    def list_providers(self) -> List[str]:
        """列出所有已注册的 Provider"""
        return list(self.providers.keys())

    def list_models(self, provider_name: str = None) -> Dict[str, List[str]]:
        """列出所有模型"""
        if provider_name:
            provider = self.providers.get(provider_name, {})
            return {provider_name: list(provider.get("models", {}).keys())}
        return {
            name: list(p.get("models", {}).keys())
            for name, p in self.providers.items()
        }
