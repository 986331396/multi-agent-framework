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
    ReviewerAgent,
    TesterAgent,
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
    "ui_reviewer": ReviewerAgent,
    "qa_tester": TesterAgent,
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

    # ===== UI 页面实现 + 双 AI 审核流程 =====
    # 实现阶段：由专业 Agent 生成代码
    "ui_page_impl": ["miniprogram_dev"],
    "ui_page_3d_impl": ["miniprogram_dev", "three_graphics_eng"],
    # 审核阶段：两个审核 Agent 并行审查
    "ui_review": ["ui_reviewer"],
    "func_test": ["qa_tester"],
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

    async def process_with_review(
        self,
        impl_task: Dict[str, Any],
        ui_spec: str,
        page_name: str,
        is_3d_page: bool = False
    ) -> Dict[str, Any]:
        """
        双 AI 审核流程：实现 → UI审核 → 功能测试 → 最终报告

        Pipeline:
          1. Implementation Agent 生成代码
          2. ReviewerAgent 审核 UI 还原度（布局、颜色、字体、组件）
          3. TesterAgent 审核功能完整性（Bug、缺失功能、性能）
          4. 汇总输出最终报告

        Args:
            impl_task: 实现任务的描述
            ui_spec: UI 设计规格详细说明（JSON字符串或路径）
            page_name: 页面名称
            is_3d_page: 是否包含 3D 功能
        """
        self.logger.info(f"[审核流程] 开始处理页面: {page_name}")
        self.logger.info(f"[审核流程] 3D页面={is_3d_page}")

        pipeline_result = {
            "page_name": page_name,
            "is_3d_page": is_3d_page,
            "pipeline_status": "running",
            "phase_1_impl": None,
            "phase_2_review": None,
            "phase_3_test": None,
            "final_verdict": None,
            "timestamp_start": "",
            "timestamp_end": "",
        }

        import time
        start_time = time.time()
        pipeline_result["timestamp_start"] = time.strftime("%Y-%m-%d %H:%M:%S")

        # ========== Phase 1: 实现 ==========
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"  Phase 1/3: 代码实现 - {page_name}")
        self.logger.info(f"{'='*60}\n")

        impl_result = await self.dispatch_task(impl_task)
        pipeline_result["phase_1_impl"] = {
            "status": impl_result.get("status", "unknown"),
            "agent": impl_result.get("agent", ""),
            "has_code": "content" in impl_result and len(impl_result.get("content", "")) > 100,
        }

        generated_code = impl_result.get("content", "")
        if not generated_code or len(generated_code) < 50:
            self.logger.error("[审核流程] Phase 1 失败：未生成有效代码")
            pipeline_result["pipeline_status"] = "failed_phase1"
            pipeline_result["final_verdict"] = {
                "verdict": "FAILED - 代码生成失败",
                "reason": "Implementation Agent 未返回有效代码",
                "recommendation": "检查 Agent 配置和 LLM API 连接"
            }
            pipeline_result["timestamp_end"] = time.strftime("%Y-%m-%d %H:%M:%S")
            return pipeline_result

        self.logger.info(f"[审核流程] Phase 1 完成，代码长度: {len(generated_code)} 字符")

        # ========== Phase 2 & 3: 双 AI 并行审核 ==========
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"  Phase 2/3: UI 还原度审核 (ReviewerAgent)")
        self.logger.info(f"  Phase 3/3: 功能测试审核 (TesterAgent)")
        self.logger.info(f"  → 两个审核 Agent 并行执行")
        self.logger.info(f"{'='*60}\n")

        # 构建审核任务
        review_task = {
            "id": f"review_{page_name}",
            "type": "ui_review",
            "description": f"审核 {page_name} 的 UI 还原度",
            "page_name": page_name,
            "ui_spec": ui_spec,
            "generated_code": generated_code,
            "screenshot_description": impl_task.get("screenshot_description", ""),
            "context": f"clothDiy 小程序 {page_name} 页面",
        }

        test_task = {
            "id": f"test_{page_name}",
            "type": "func_test",
            "description": f"测试 {page_name} 的功能和代码质量",
            "page_name": page_name,
            "generated_code": generated_code,
            "requirements": impl_task.get("description", ""),
            "is_3d_page": is_3d_page,
            "context": f"clothDiy 小程序 {page_name} 页面 {'(含3D功能)' if is_3d_page else ''}",
        }

        # 并行执行两个审核
        review_coro = self.dispatch_task_to("ui_reviewer", review_task)
        test_coro = self.dispatch_task_to("qa_tester", test_task)

        review_result, test_result = await asyncio.gather(
            review_coro, test_coro, return_exceptions=True
        )

        # 处理审核结果
        if isinstance(review_result, Exception):
            self.logger.error(f"[审核流程] UI审核异常: {review_result}")
            pipeline_result["phase_2_review"] = {"status": "error", "error": str(review_result)}
        else:
            pipeline_result["phase_2_review"] = review_result
            self.logger.info(f"[审核流程] Phase 2 (UI审核) 完成")

        if isinstance(test_result, Exception):
            self.logger.error(f"[审核流程] 功能测试异常: {test_result}")
            pipeline_result["phase_3_test"] = {"status": "error", "error": str(test_result)}
        else:
            pipeline_result["phase_3_test"] = test_result
            self.logger.info(f"[审核流程] Phase 3 (功能测试) 完成")

        # ========== 汇总最终报告 ==========
        elapsed = time.time() - start_time
        pipeline_result["timestamp_end"] = time.strftime("%Y-%m-%d %H:%M:%S")
        pipeline_result["elapsed_seconds"] = round(elapsed, 1)

        # 解析审核分数
        review_score = self._extract_score(pipeline_result.get("phase_2_review", {}))
        test_score = self._extract_score(pipeline_result.get("phase_3_test", {}))
        avg_score = (review_score + test_score) / 2 if (review_score > 0 and test_score > 0) else 0

        # 生成最终判定
        if avg_score >= 80 and review_score >= 75 and test_score >= 75:
            verdict_status = "PASS"
            verdict_msg = f"通过 ✅ — UI还原度({review_score}分) + 功能测试({test_score}分)，综合{avg_score:.0f}分"
        elif avg_score >= 60:
            verdict_status = "CONDITIONAL_PASS"
            verdict_msg = f"有条件通过 ⚠️ — 需修复 CRITICAL 和 MAJOR 级别问题后可上线 (UI:{review_score}分, 测试:{test_score}分)"
        else:
            verdict_status = "FAIL"
            verdict_msg = f"不通过 ❌ — 需要重新实现 (UI:{review_score}分, 测试:{test_score}分)"

        pipeline_result["final_verdict"] = {
            "status": verdict_status,
            "message": verdict_msg,
            "scores": {
                "ui_review": review_score,
                "func_test": test_score,
                "average": round(avg_score, 1),
            },
            "critical_issues_count": self._count_critical_issues(pipeline_result),
            "recommendation": self._generate_recommendation(verdict_status, pipeline_result),
        }
        pipeline_result["pipeline_status"] = "completed"

        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"  审核流程完成！")
        self.logger.info(f"  最终判定: {verdict_msg}")
        self.logger.info(f"  耗时: {elapsed:.1f}s")
        self.logger.info(f"{'='*60}\n")

        return pipeline_result

    async def dispatch_task_to(self, agent_key: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """将任务分派给指定 Agent"""
        agent = self.registered_agents.get(agent_key)
        if not agent:
            raise ValueError(f"Agent not found: {agent_key}")
        self.logger.info(f"分发到 [{agent_key}]: {task.get('id')}")
        return await agent.execute_with_retry(task)

    def _extract_score(self, result: Dict[str, Any]) -> int:
        """从审核结果中提取分数"""
        try:
            content = result.get("result", {}).get("content", result.get("content", ""))
            if isinstance(content, str):
                import json, re
                match = re.search(r'"(overall_score|test_score)"\s*:\s*(\d+)', content)
                if match:
                    return int(match.group(2))
            elif isinstance(content, dict):
                return content.get("overall_score", content.get("test_score", 0))
        except Exception:
            pass
        return 0

    def _count_critical_issues(self, pipeline_result: Dict[str, Any]) -> int:
        """统计严重问题数量"""
        count = 0
        for phase_key in ["phase_2_review", "phase_3_test"]:
            phase = pipeline_result.get(phase_key, {})
            result_content = phase.get("result", {}).get("content", "") if isinstance(phase.get("result"), dict) else phase.get("content", "")
            if isinstance(result_content, str):
                count += result_content.lower().count('"critical"')
        return count

    def _generate_recommendation(self, status: str, pipeline_result: Dict[str, Any]) -> str:
        """根据审核结果生成建议"""
        if status == "PASS":
            return "代码质量达标，可以进入下一阶段开发。建议进行真机测试验证 3D 性能。"
        elif status == "CONDITIONAL_PASS":
            issues = self._count_critical_issues(pipeline_result)
            return f"发现 {issues} 个关键问题，请优先修复 CRITICAL 和 MAJOR 级别问题后重新提交审核。"
        else:
            return "代码质量不满足要求，建议重新分析设计规格并重写代码，特别关注 3D 交互功能的完整实现。"

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
