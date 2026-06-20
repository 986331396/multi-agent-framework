"""
产品经理 Agent
负责需求分析、PRD撰写、用户故事、交互流程设计
"""

from typing import Any, Dict

from ..base_agent import BaseAgent


class ProductAgent(BaseAgent):
    """
    产品经理 Agent

    专业领域: 服装电商、3D定制化产品、C2M平台
    核心职责:
      1. 需求分析与 PRD 撰写
      2. 用户故事与验收标准
      3. 交互流程设计
      4. 项目排期与里程碑
      5. 竞品分析
    """

    async def analyze_requirement(self, requirement: str) -> Dict[str, Any]:
        """分析用户需求，输出结构化需求文档"""
        prompt = f"""
请分析以下产品需求，输出结构化的需求分析：

需求: {requirement}

请包含:
1. 需求背景与目标
2. 目标用户画像
3. 核心功能点列表（按优先级排序）
4. 非功能性需求（性能/安全/兼容性）
5. 验收标准
6. 风险点与依赖项
"""
        content = await self.call_llm(prompt)
        return {"analysis": content}

    async def write_prd(self, feature_name: str, description: str) -> Dict[str, Any]:
        """撰写 PRD 文档"""
        prompt = f"""
请为以下功能撰写详细 PRD 文档:

功能名称: {feature_name}
功能描述: {description}

PRD 需包含:
1. 功能概述
2. 用户故事 (As a... I want... So that...)
3. 详细功能说明（含流程图描述）
4. 数据模型设计建议
5. 接口需求
6. 交互设计要点
7. 异常处理与边界情况
"""
        content = await self.call_llm(prompt)
        return {"prd": content}

    async def design_user_flow(self, flow_name: str) -> Dict[str, Any]:
        """设计用户交互流程"""
        prompt = f"""
请设计用户交互流程: {flow_name}

输出格式:
1. 流程概述
2. 角色定义
3. 前置条件
4. 详细步骤（含分支与异常流）
5. 状态流转图描述
6. 关键交互节点说明
"""
        content = await self.call_llm(prompt)
        return {"user_flow": content}

    async def plan_milestone(self, project_scope: str) -> Dict[str, Any]:
        """制定项目里程碑计划"""
        prompt = f"""
请为以下项目范围制定里程碑计划:

项目范围: {project_scope}

请按 Phase 输出:
1. 每个 Phase 的目标
2. 核心交付物
3. 任务分解 (WBS)
4. 人员需求
5. 时间估算
6. 依赖关系
"""
        content = await self.call_llm(prompt)
        return {"milestone_plan": content}

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理产品任务"""
        task_type = task.get("subtype", "analyze")
        description = task.get("description", "")

        if task_type == "analyze":
            result = await self.analyze_requirement(description)
        elif task_type == "prd":
            result = await self.write_prd(
                task.get("feature_name", ""),
                description
            )
        elif task_type == "user_flow":
            result = await self.design_user_flow(description)
        elif task_type == "milestone":
            result = await self.plan_milestone(description)
        else:
            result = await self.analyze_requirement(description)

        return self.format_result(task, result.get("analysis", str(result)), result)
