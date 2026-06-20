"""
Agent 基类模块
定义所有 Agent 的公共接口和基础功能
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """
    Agent 抽象基类

    所有具体 Agent 都必须继承此类并实现 process 方法。
    提供统一的初始化、消息处理和错误管理能力。
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("agents", {})
        self.agent_config = {}
        self.name = "BaseAgent"
        self.role = "通用助手"
        self.description = ""
        self._initialize()

    def _initialize(self):
        """从配置中初始化 Agent 属性"""
        agent_type = self.__class__.__name__.lower().replace("agent", "")
        if agent_type in self.config:
            self.agent_config = self.config[agent_type]
            self.name = self.agent_config.get("name", self.name)
            self.role = self.agent_config.get("role", self.role)
            self.description = self.agent_config.get("description", "")

        self.logger = logging.getLogger(f"agent.{self.name}")
        self.logger.info(f"Agent 初始化完成: {self.name} - {self.role}")

    @abstractmethod
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理任务的核心方法（子类必须实现）

        Args:
            task: 任务字典，包含任务类型、描述等

        Returns:
            处理结果字典
        """
        pass

    async def execute_with_retry(
        self,
        task: Dict[str, Any],
        max_retries: int = 3,
        retry_delay: float = 2.0
    ) -> Dict[str, Any]:
        """带重试机制的任务执行"""
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                self.logger.debug(f"执行任务 (尝试 {attempt + 1}/{max_retries + 1})")
                return await self.process(task)
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"任务执行失败 (尝试 {attempt + 1}): {e}"
                )
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * (attempt + 1))

        raise last_error

    def format_message(self, content: str, metadata: Optional[Dict] = None) -> Dict:
        """格式化标准化消息"""
        return {
            "sender": self.name,
            "content": content,
            "metadata": metadata or {},
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, role={self.role})>"
