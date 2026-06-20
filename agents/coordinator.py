"""
协调者 Agent 模块
负责任务分解、分配调度和结果整合，支持多 LLM Provider 和专业化 Agent 团队
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Type

from .base_agent import BaseAgent
from .specialists import (
    ProductAgent,
    UIUXAgent,
    MiniProgramAgent,
    AdminFrontendAgent,
    ThreeDGraphicsAgent,
    GoBackendAgent,
    MicroserviceAgent,
    DatabaseAgent,
    DevOpsAgent,
    GarmentModelingAgent,
    SupplyChainAgent,
    QAAgent,
)
from utils.llm_client import LLMClient


# Agent 类型注册表：agent_key -> Agent 类
AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {
    "product_manager": ProductAgent,
    "ui_designer": UIUXAgent,
    "miniprogram_dev": MiniProgramAgent,
    "admin_frontend_dev": AdminFrontendAgent,
    "three_graphics_eng": ThreeDGraphicsAgent,
    "go_backend_dev": GoBackendAgent,
    "microservice_dev": MicroserviceAgent,
    "database_eng": DatabaseAgent,
    "devops_eng": DevOpsAgent,
    "garment_modeling": GarmentModelingAgent,
    "supply_chain_expert": SupplyChainAgent,
    "qa_engineer": QAAgent,
}

# 任务类型 → Agent 映射规则
TASK_ROUTING_RULES: Dict[str, List[str]] = {
    # 产品类任务
    "requirement_analysis": ["product_manager"],
    "prd": ["product_manager"],
    "user_flow": ["product_manager"],
    "milestone": ["product_manager"],
    # 设计类任务
    "ui_design": ["ui_designer"],
    "design_system": ["ui_designer"],
    "component_design": ["ui_designer"],
    # 小程序前端
    "miniprogram_page": ["miniprogram_dev"],
    "miniprogram_3d": ["miniprogram_dev", "three_graphics_eng"],
    "miniprogram_optimize": ["miniprogram_dev"],
    # 管理后台
    "admin_view": ["admin_frontend_dev"],
    "admin_crud": ["admin_frontend_dev"],
    # 3D 图形
    "smplx_mapping": ["three_graphics_eng"],
    "threejs_scene": ["three_graphics_eng"],
    "draco_compression": ["three_graphics_eng"],
    "garment_skinning": ["three_graphics_eng", "garment_modeling"],
    # 后端
    "api_module": ["go_backend_dev"],
    "go_model": ["go_backend_dev"],
    "middleware": ["go_backend_dev"],
    "api_spec": ["go_backend_dev", "product_manager"],
    # 微服务
    "microservice_design": ["microservice_dev"],
    "proto_definition": ["microservice_dev"],
    "rabbitmq": ["microservice_dev"],
    "api_gateway": ["microservice_dev"],
    # 数据库
    "db_schema": ["database_eng"],
    "query_optimize": ["database_eng"],
    "elasticsearch": ["database_eng"],
    "redis_cache": ["database_eng"],
    # DevOps
    "dockerfile": ["devops_eng"],
    "docker_compose": ["devops_eng"],
    "k8s": ["devops_eng"],
    "cicd": ["devops_eng"],
    "monitoring": ["devops_eng"],
    # 3D 建模
    "blender_workflow": ["garment_modeling"],
    "blender_script": ["garment_modeling"],
    "skinning_guide": ["garment_modeling"],
    "gltf_export": ["garment_modeling"],
    # 供应链
    "order_state_machine": ["supply_chain_expert"],
    "factory_matching": ["supply_chain_expert"],
    "craft_sheet": ["supply_chain_expert"],
    "progress_tracking": ["supply_chain_expert"],
    # 测试
    "unit_test": ["qa_engineer"],
    "api_test": ["qa_engineer"],
    "load_test": ["qa_engineer"],
    "3d_compat_test": ["qa_engineer"],
    # 复合任务
    "full_stack_feature": ["product_manager", "go_backend_dev", "miniprogram_dev"],
    "new_module": ["product_manager", "database_eng", "go_backend_dev", "qa_engineer"],
    "deployment": ["devops_eng", "qa_engineer"],
}


class Coordinator(BaseAgent):
    """
    协调者 Agent

    核心职责:
    1. 接收高层任务并分解为子任务
    2. 根据任务类型路由到对应的专业 Agent
    3. 并发执行子任务
    4. 整合结果并生成最终输出
    """

    def __init__(self, config: Dict[str, Any], llm_client: Optional[LLMClient] = None):
        super().__init__(config, llm_client)
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.llm_client = llm_client
        self._auto_register_all()

    def _auto_register_all(self):
        """自动注册所有配置中定义的 Agent"""
        for agent_key, agent_class in AGENT_REGISTRY.items():
            if agent_key in self.agents_config:
                agent = agent_class(self.config, self.llm_client)
                self.register_agent(agent_key, agent)

    def register_agent(self, agent_key: str, agent: BaseAgent):
        """注册一个 Agent"""
        self.registered_agents[agent_key] = agent
        model_info = f"{agent.llm_provider}/{agent.llm_model}"
        self.logger.info(
            f"注册 Agent: {agent_key} ({agent.name} - {agent.role}) [{model_info}]"
        )

    async def decompose_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """将复杂任务分解为子任务"""
        task_type = task.get("type", "general")
        description = task.get("description", "")
        subtype = task.get("subtype", "")

        self.logger.info(f"分解任务: type={task_type}, subtype={subtype}")

        # 查找路由规则
        route_key = subtype if subtype else task_type
        agent_keys = TASK_ROUTING_RULES.get(route_key, [])

        if not agent_keys:
            # 使用 LLM 智能分析任务应该分配给哪些 Agent
            agent_keys = await self._smart_route(task)

        if not agent_keys:
            # 最终回退：分配给产品经理分析
            agent_keys = ["product_manager"]

        subtasks = []
        for i, agent_key in enumerate(agent_keys):
            subtasks.append({
                "id": f"{route_key}_{agent_key}_{i}",
                "type": task_type,
                "subtype": subtype or task_type,
                "agent": agent_key,
                "description": description,
                "context": task.get("context", ""),
                "priority": task.get("priority", "medium"),
                "feature_name": task.get("feature_name", ""),
                "page_name": task.get("page_name", ""),
                "module_name": task.get("module_name", ""),
                "model_name": task.get("model_name", ""),
                "service_name": task.get("service_name", ""),
                "component_name": task.get("component_name", ""),
                "index_name": task.get("index_name", ""),
                "project_name": task.get("project_name", ""),
                "view_name": task.get("view_name", ""),
            })

        self.logger.info(f"任务已分解为 {len(subtasks)} 个子任务，分配给: {agent_keys}")
        return subtasks

    async def _smart_route(self, task: Dict[str, Any]) -> List[str]:
        """使用 LLM 智能分析任务应该分配给哪些 Agent"""
        available_agents = {
            key: {
                "name": cfg.get("name", ""),
                "role": cfg.get("role", ""),
                "description": cfg.get("description", ""),
            }
            for key, cfg in self.agents_config.items()
            if key != "coordinator"
        }

        prompt = f"""
请分析以下任务应该分配给哪些专业 Agent 处理:

任务: {task.get('description', '')}
任务类型: {task.get('type', 'unknown')}

可用的 Agent 列表:
{available_agents}

请只返回 agent_key 列表（JSON数组格式），如: ["go_backend_dev", "qa_engineer"]
"""
        try:
            content = await self.call_llm(prompt)
            # 尝试解析 JSON 数组
            import json
            import re
            match = re.search(r'\[.*?\]', content, re.DOTALL)
            if match:
                agent_keys = json.loads(match.group())
                # 过滤掉无效的 key
                valid_keys = [k for k in agent_keys if k in AGENT_REGISTRY]
                if valid_keys:
                    return valid_keys
        except Exception as e:
            self.logger.warning(f"智能路由失败: {e}")

        return []

    async def dispatch_task(self, subtask: Dict[str, Any]) -> Dict[str, Any]:
        """将子任务分派给对应的 Agent 执行"""
        agent_key = subtask.get("agent")
        agent = self.registered_agents.get(agent_key)

        if not agent:
            error_msg = f"未找到可用的 Agent: {agent_key}"
            self.logger.error(error_msg)
            return {"error": error_msg, "subtask_id": subtask.get("id")}

        self.logger.info(
            f"分发任务 '{subtask['id']}' 给 {agent_key} ({agent.name})"
        )
        result = await agent.execute_with_retry(subtask)
        return result

    async def integrate_results(
        self,
        task: Dict[str, Any],
        subtask_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """整合所有子任务的执行结果"""
        self.logger.info(f"整合 {len(subtask_results)} 个子任务结果")

        integrated = {
            "status": "completed",
            "original_task": task.get("description", ""),
            "task_type": task.get("type", ""),
            "summary": "",
            "agent_results": {},
            "recommendations": [],
            "agents_involved": [],
        }

        for result in subtask_results:
            agent_name = result.get("agent", "unknown")
            integrated["agent_results"][agent_name] = result
            integrated["agents_involved"].append({
                "agent": agent_name,
                "role": result.get("role", ""),
                "model": result.get("llm_info", {}).get("model", ""),
                "status": result.get("status", "unknown"),
            })
            if "content" in result and isinstance(result["content"], str):
                integrated["summary"] += f"\n[{agent_name}] {result['content'][:200]}...\n"

        integrated["summary"] = integrated["summary"].strip()
        self.logger.info(
            f"结果整合完成，涉及 {len(integrated['agents_involved'])} 个 Agent"
        )
        return integrated

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理协调任务的主流程"""
        self.logger.info(f"Coordinator 开始处理: {task.get('type')}")

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
                    "agent": subtasks[i]["agent"],
                    "subtask_id": subtasks[i]["id"],
                    "status": "failed",
                })
            else:
                valid_results.append(result)

        # 3. 整合结果
        final_result = await self.integrate_results(task, valid_results)
        return final_result

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """公共执行接口"""
        return await self.execute_with_retry(task)

    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有已注册的 Agent"""
        return [
            {
                "key": key,
                "name": agent.name,
                "role": agent.role,
                "description": agent.description,
                "llm": f"{agent.llm_provider}/{agent.llm_model}",
            }
            for key, agent in self.registered_agents.items()
        ]
