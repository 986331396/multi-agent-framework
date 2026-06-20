"""
协调者 Agent 模块
负责任务分解、分配调度和结果整合
"""

import asyncio
import logging
from typing import Any, Dict, List

from .base_agent import BaseAgent


class Coordinator(BaseAgent):
    """
    协调者 Agent

    核心职责：
    1. 接收高层任务并分解为子任务
    2. 将子任务分配给合适的 Agent
    3. 收集各 Agent 的执行结果
    4. 整合结果并生成最终输出
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.results: Dict[str, Any] = {}

    def register_agent(self, name: str, agent: BaseAgent):
        """注册一个可用的 Agent"""
        self.registered_agents[name] = agent
        self.logger.info(f"注册可用 Agent: {name} ({agent.role})")

    async def decompose_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        将复杂任务分解为子任务

        分解策略：
        - research 类任务分配给 ResearchAgent
        - coding 类任务分配给 CodingAgent
        - 复合任务同时分配给多个 Agent
        """
        task_type = task.get("type", "general")
        description = task.get("description", "")
        subtasks = []

        self.logger.info(f"分解任务: {task_type}")

        # 根据任务类型分解
        if task_type in ("research", "analysis", "complex_task"):
            subtasks.append({
                "id": f"{task_type}_research",
                "type": "research",
                "agent": "researcher",
                "description": f"研究分析: {description}",
                "priority": task.get("priority", "medium"),
            })

        if task_type in ("coding", "development", "complex_task"):
            subtasks.append({
                "id": f"{task_type}_coding",
                "type": "coding",
                "agent": "coder",
                "description": f"技术实现: {description}",
                "priority": task.get("priority", "medium"),
            })

        if not subtasks:
            # 默认分解为研究和编码两个阶段
            subtasks.extend([
                {
                    "id": "default_research",
                    "type": "research",
                    "agent": "researcher",
                    "description": f"初步调研: {description}",
                },
                {
                    "id": "default_coding",
                    "type": "coding",
                    "agent": "coder",
                    "description": f"方案设计: {description}",
                },
            ])

        self.logger.info(f"任务已分解为 {len(subtasks)} 个子任务")
        return subtasks

    async def dispatch_task(self, subtask: Dict[str, Any]) -> Dict[str, Any]:
        """将子任务分派给对应的 Agent 执行"""
        agent_name = subtask.get("agent")
        agent = self.registered_agents.get(agent_name)

        if not agent:
            error_msg = f"未找到可用的 Agent: {agent_name}"
            self.logger.error(error_msg)
            return {"error": error_msg, "subtask_id": subtask.get("id")}

        self.logger.info(f"分发任务 '{subtask['id']}' 给 {agent_name}")
        result = await agent.execute_with_retry(subtask)

        self.results[subtask["id"]] = result
        return result

    async def integrate_results(
        self,
        task: Dict[str, Any],
        subtask_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        整合所有子任务的执行结果

        生成包含各部分贡献的完整报告
        """
        self.logger.info(f"整合 {len(subtask_results)} 个子任务结果")

        integrated = {
            "status": "completed",
            "original_task": task.get("description", ""),
            "summary": "",
            "details": {},
            "recommendations": [],
        }

        for result in subtask_results:
            task_id = result.get("subtask_id", "unknown")
            integrated["details"][task_id] = result
            if "summary" in result:
                integrated["summary"] += result["summary"] + "\n"
            if "recommendations" in result:
                integrated["recommendations"].extend(
                    result["recommendations"]
                )

        integrated["summary"] = integrated["summary"].strip()
        self.logger.info("结果整合完成")
        return integrated

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理协调任务的主流程"""
        self.logger.info(f"开始处理协调任务: {task.get('type')}")

        # 1. 分解任务
        subtasks = await self.decompose_task(task)

        # 2. 并发执行所有子任务
        tasks = [self.dispatch_task(st) for st in subtasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"子任务 {subtasks[i]['id']} 异常: {result}")
                valid_results.append({
                    "error": str(result),
                    "subtask_id": subtasks[i]["id"],
                })
            else:
                valid_results.append(result)

        # 3. 整合结果
        final_result = await self.integrate_results(task, valid_results)
        return final_result

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """公共执行接口"""
        return await self.execute_with_retry(task)
