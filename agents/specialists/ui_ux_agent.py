"""
UI/UX 设计师 Agent
负责界面设计、设计系统、配色方案、交互原型
"""

from typing import Any, Dict

from ..base_agent import BaseAgent


class UIUXAgent(BaseAgent):
    """
    UI/UX 设计师 Agent

    专业领域: Fashion-Tech 风格、设计系统、交互原型
    核心职责:
      1. 界面视觉设计
      2. 设计系统搭建
      3. 配色方案与排版规范
      4. 交互原型描述
      5. 响应式适配方案
    """

    async def design_page(self, page_name: str, requirements: str) -> Dict[str, Any]:
        """设计页面视觉方案"""
        prompt = f"""
请设计以下页面的完整视觉方案:

页面名称: {page_name}
需求描述: {requirements}

请输出:
1. 页面布局结构（区域划分）
2. 配色方案（主色/辅色/背景色/文字色，含 HEX 值）
3. 字体规范（标题/正文/辅助文字的大小与字重）
4. 间距与圆角规范
5. 组件样式说明（按钮/卡片/输入框等）
6. 交互动效描述
7. 响应式适配建议

设计风格定位: Fashion-Tech in Motion（高级感、动态、精致）
"""
        content = await self.call_llm(prompt)
        return {"design_spec": content}

    async def build_design_system(self, project_name: str) -> Dict[str, Any]:
        """搭建设计系统"""
        prompt = f"""
请为项目「{project_name}」搭建完整的设计系统:

1. 色彩系统（品牌色/功能色/中性色/语义色）
2. 字体系统（字体族/字号梯度/行高/字重）
3. 间距系统（基础间距单位/间距梯度）
4. 圆角与阴影系统
5. 组件规范（按钮/标签/卡片/导航/弹窗/表单）
6. 图标与插画规范
7. 动效规范（过渡时间/缓动函数）
8. 暗色模式适配
"""
        content = await self.call_llm(prompt)
        return {"design_system": content}

    async def design_component(self, component_name: str, spec: str) -> Dict[str, Any]:
        """设计单个组件"""
        prompt = f"""
请设计组件「{component_name}」的详细规范:

需求: {spec}

输出:
1. 组件结构（DOM/WXML 层级）
2. 状态变体（default/hover/active/disabled/loading/error）
3. 尺寸变体（small/medium/large）
4. 样式代码片段（CSS/WXSS）
5. 交互行为说明
6. 无障碍适配
"""
        content = await self.call_llm(prompt)
        return {"component_spec": content}

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理设计任务"""
        task_type = task.get("subtype", "design_page")
        description = task.get("description", "")

        if task_type == "design_page":
            result = await self.design_page(
                task.get("page_name", ""),
                description
            )
        elif task_type == "design_system":
            result = await self.build_design_system(description)
        elif task_type == "component":
            result = await self.design_component(
                task.get("component_name", ""),
                description
            )
        else:
            result = await self.design_page(description, description)

        return self.format_result(task, str(result), result)
