"""
Go后端工程师 Agent
负责 Gin框架、GORM、RESTful API、JWT认证
"""

from typing import Any, Dict

from ..base_agent import BaseAgent


class GoBackendAgent(BaseAgent):
    """
    Go后端工程师 Agent

    专业领域: Go 1.21+、Gin、GORM、PostgreSQL、Redis、JWT
    核心职责:
      1. RESTful API 设计与实现
      2. 数据模型定义（GORM）
      3. 业务逻辑层开发
      4. 中间件开发（认证/日志/限流）
      5. WebSocket 实时通信
    """

    async def create_api_module(self, module_name: str, fields: str) -> Dict[str, Any]:
        """创建完整的 API 模块"""
        prompt = f"""
请创建 Go 后端 API 模块「{module_name}」:

字段定义: {fields}

请输出完整代码:
1. models/{module_name}.go - GORM 数据模型
2. services/{module_name}_service.go - 业务逻辑层
3. routers/{module_name}_router.go - 路由定义
4. dto/{module_name}_dto.go - 请求/响应 DTO
5. middlewares 相关中间件（如需要）

技术栈: Gin + GORM + PostgreSQL
规范:
- 使用 go mod 管理依赖
- 公开函数必须有 Godoc 注释
- 禁止 SELECT *，必须指定字段
- 每个 Service 方法必须有错误处理
"""
        content = await self.call_llm(prompt)
        return {"api_code": content}

    async def create_model(self, model_name: str, fields: str) -> Dict[str, Any]:
        """创建数据模型"""
        prompt = f"""
请创建 GORM 数据模型「{model_name}」:

字段: {fields}

输出 models/{model_name.lower()}.go:
1. Struct 定义（含 GORM 标签）
2. JSON 标签
3. 表名方法 (TableName)
4. 常用查询方法
5. 验证方法
"""
        content = await self.call_llm(prompt)
        return {"model_code": content}

    async def create_middleware(self, middleware_name: str, description: str) -> Dict[str, Any]:
        """创建中间件"""
        prompt = f"""
请创建 Gin 中间件「{middleware_name}」:

描述: {description}

输出:
1. middlewares/{middleware_name}.go 完整代码
2. 使用示例
3. 配置说明
"""
        content = await self.call_llm(prompt)
        return {"middleware_code": content}

    async def design_api_spec(self, module_name: str, description: str) -> Dict[str, Any]:
        """设计 API 接口文档"""
        prompt = f"""
请为模块「{module_name}」设计 RESTful API 接口文档:

模块描述: {description}

输出:
1. 接口列表（方法/路径/描述/认证要求）
2. 请求参数说明（Query/Body/Path）
3. 响应格式（成功/错误）
4. 状态码定义
5. 分页/排序/筛选规范
6. 错误码表
"""
        content = await self.call_llm(prompt)
        return {"api_spec": content}

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理后端任务"""
        task_type = task.get("subtype", "api_module")
        description = task.get("description", "")

        if task_type == "api_module":
            result = await self.create_api_module(
                task.get("module_name", ""),
                description
            )
        elif task_type == "model":
            result = await self.create_model(
                task.get("model_name", ""),
                description
            )
        elif task_type == "middleware":
            result = await self.create_middleware(
                task.get("middleware_name", ""),
                description
            )
        elif task_type == "api_spec":
            result = await self.design_api_spec(
                task.get("module_name", ""),
                description
            )
        else:
            result = await self.create_api_module(description, description)

        return self.format_result(task, str(result), result)
