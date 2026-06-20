"""
管理后台前端工程师 Agent
负责 Vue3 + Ant Design 后台管理系统开发
"""

from typing import Any, Dict

from ..base_agent import BaseAgent


class AdminFrontendAgent(BaseAgent):
    """
    管理后台前端工程师 Agent

    专业领域: Vue3 Composition API、Ant Design Vue、后台管理系统
    核心职责:
      1. 后台管理页面开发（CRUD界面）
      2. Vue3 组件开发
      3. API 请求封装
      4. 权限路由管理
      5. 后台3D预览集成
    """

    async def create_view(self, view_name: str, requirements: str) -> Dict[str, Any]:
        """创建后台管理视图"""
        prompt = f"""
请创建 Vue3 管理后台视图「{view_name}」:

需求: {requirements}

请输出:
1. Vue3 SFC 代码（<script setup> + <template> + <style>）
2. API 请求封装代码
3. 路由配置
4. 使用 Ant Design Vue 组件

规范:
- 使用 Composition API (<script setup>)
- 组件命名 PascalCase
- API 请求统一在 src/api/ 封装
- 路由统一在 src/router/ 管理
"""
        content = await self.call_llm(prompt)
        return {"view_code": content}

    async def create_crud_module(self, module_name: str, fields: str) -> Dict[str, Any]:
        """创建完整的 CRUD 模块"""
        prompt = f"""
请创建管理后台 CRUD 模块「{module_name}」:

字段定义: {fields}

请输出完整代码:
1. 列表页（含搜索/筛选/分页/批量操作）
2. 新建/编辑弹窗表单
3. 详情页
4. API 封装（增删改查）
5. 类型定义（TypeScript interface）
6. 路由配置

使用 Vue3 + Ant Design Vue + TypeScript
"""
        content = await self.call_llm(prompt)
        return {"crud_code": content}

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理后台前端任务"""
        task_type = task.get("subtype", "create_view")
        description = task.get("description", "")

        if task_type == "create_view":
            result = await self.create_view(
                task.get("view_name", ""),
                description
            )
        elif task_type == "crud":
            result = await self.create_crud_module(
                task.get("module_name", ""),
                description
            )
        else:
            result = await self.create_view(description, description)

        return self.format_result(task, str(result), result)
