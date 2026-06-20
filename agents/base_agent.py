"""
Agent 基类模块
定义所有 Agent 的公共接口和基础功能，支持多 LLM Provider
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from utils.llm_client import LLMClient


class BaseAgent(ABC):
    """
    Agent 抽象基类

    所有具体 Agent 都必须继承此类并实现 process 方法。
    提供：LLM 调用、任务处理、消息格式化和错误重试能力。
    """

    def __init__(self, config: Dict[str, Any], llm_client: Optional[LLMClient] = None):
        self.config = config
        self.llm_client = llm_client
        self.agents_config = config.get("agents", {})
        self.llm_providers_config = config.get("llm_providers", {})

        # Agent 自身配置
        self.agent_key: str = ""
        self.name: str = "BaseAgent"
        self.role: str = "通用助手"
        self.description: str = ""
        self.system_prompt: str = ""
        self.llm_provider: str = "deepseek"
        self.llm_model: str = "deepseek-chat"
        self.expertise: List[str] = []  # 专业领域标签
        self.capabilities: List[str] = []  # 能力清单

        self._initialize()

    def _initialize(self):
        """从配置中初始化 Agent 属性"""
        # 根据类名推断 agent_key
        # 如 GoBackendAgent -> go_backend_dev
        class_name = self.__class__.__name__
        # 在 agents_config 中查找匹配的配置
        for key, agent_cfg in self.agents_config.items():
            if agent_cfg.get("name") == class_name:
                self.agent_key = key
                self._apply_config(agent_cfg)
                break

        if not self.agent_key:
            # 回退：使用类名小写
            self.agent_key = class_name.lower()

        self.logger = logging.getLogger(f"agent.{self.name}")
        self.logger.info(f"Agent 初始化: {self.name} - {self.role}")

    def _apply_config(self, agent_cfg: Dict[str, Any]):
        """应用 Agent 配置"""
        self.name = agent_cfg.get("name", self.name)
        self.role = agent_cfg.get("role", self.role)
        self.description = agent_cfg.get("description", self.description)
        self.system_prompt = agent_cfg.get("system_prompt", "")
        self.llm_provider = agent_cfg.get("llm_provider", self.llm_provider)
        self.llm_model = agent_cfg.get("llm_model", self.llm_model)
        self.expertise = agent_cfg.get("expertise", [])
        self.capabilities = agent_cfg.get("capabilities", [])

    async def call_llm(self, user_message: str, **kwargs) -> str:
        """
        调用 LLM 生成回复

        自动注入 system_prompt，使用 Agent 配置的 provider 和 model。
        """
        if not self.llm_client:
            self.logger.warning(f"{self.name} 无 LLM 客户端，返回模拟响应")
            return f"[模拟响应 - {self.name}] 无 LLM 客户端配置"

        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": user_message})

        result = await self.llm_client.chat(
            self.llm_provider,
            self.llm_model,
            messages,
            **kwargs
        )
        return result.get("content", "")

    async def call_llm_with_context(
        self, user_message: str, context: str, **kwargs
    ) -> str:
        """带额外上下文的 LLM 调用"""
        full_message = f"## 项目上下文\n{context}\n\n## 任务\n{user_message}"
        return await self.call_llm(full_message, **kwargs)

    @abstractmethod
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务的核心方法（子类必须实现）"""
        pass

    async def execute_with_retry(
        self,
        task: Dict[str, Any],
        max_retries: int = None,
        retry_delay: float = 2.0
    ) -> Dict[str, Any]:
        """带重试机制的任务执行"""
        task_settings = self.config.get("task_settings", {})
        max_retries = max_retries or task_settings.get("max_retries", 3)
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                self.logger.debug(
                    f"执行任务 (尝试 {attempt + 1}/{max_retries + 1})"
                )
                return await self.process(task)
            except Exception as e:
                last_error = e
                self.logger.warning(f"任务执行失败 (尝试 {attempt + 1}): {e}")
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * (attempt + 1))

        raise last_error

    def format_result(
        self,
        task: Dict[str, Any],
        content: str,
        extras: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """格式化标准化输出结果"""
        result = {
            "agent": self.name,
            "role": self.role,
            "subtask_id": task.get("id", "unknown"),
            "status": "completed",
            "content": content,
            "llm_info": {
                "provider": self.llm_provider,
                "model": self.llm_model,
            },
            "timestamp": datetime.now().isoformat(),
        }
        if extras:
            result.update(extras)
        return result

    def format_message(self, content: str, metadata: Optional[Dict] = None) -> Dict:
        """格式化标准化消息"""
        return {
            "sender": self.name,
            "role": self.role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"name={self.name}, role={self.role}, "
            f"model={self.llm_provider}/{self.llm_model})>"
        )
