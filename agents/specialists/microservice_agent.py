"""
微服务工程师 Agent
负责 go-zero微服务、gRPC、服务发现、消息队列
"""

from typing import Any, Dict

from ..base_agent import BaseAgent


class MicroserviceAgent(BaseAgent):
    """
    微服务工程师 Agent

    专业领域: go-zero、gRPC、Protobuf、RabbitMQ、服务发现
    核心职责:
      1. 微服务架构设计与拆分
      2. gRPC 服务定义与实现
      3. Protobuf 接口定义
      4. RabbitMQ 消息队列集成
      5. API 网关配置
      6. 服务注册与发现
    """

    async def design_microservice(self, service_name: str, description: str) -> Dict[str, Any]:
        """设计微服务架构"""
        prompt = f"""
请设计微服务「{service_name}」的完整架构:

服务描述: {description}

输出:
1. 服务职责定义
2. Protobuf 接口定义 (.proto 文件)
3. go-zero 服务端代码结构
4. 数据库独立存储方案
5. 与其他服务的通信方式（gRPC/消息队列）
6. 服务注册与发现配置
7. 配置文件模板 (yaml)
"""
        content = await self.call_llm(prompt)
        return {"architecture": content}

    async def create_proto(self, service_name: str, methods: str) -> Dict[str, Any]:
        """创建 Protobuf 定义"""
        prompt = f"""
请为服务「{service_name}」创建 Protobuf 定义:

方法列表: {methods}

输出:
1. 完整的 .proto 文件
2. 请求/响应消息定义
3. 服务方法定义
4. go-zero 生成命令
5. 客户端调用示例
"""
        content = await self.call_llm(prompt)
        return {"proto_code": content}

    async def setup_rabbitmq(self, use_case: str) -> Dict[str, Any]:
        """配置 RabbitMQ 消息队列"""
        prompt = f"""
请为「{use_case}」配置 RabbitMQ 消息队列方案:

输出:
1. Go 代码：生产者与消费者实现
2. 队列/交换机/路由键定义
3. 消息序列化方案（JSON/Protobuf）
4. 重试与死信队列配置
5. 消费者并发控制
6. 监控与告警建议
"""
        content = await self.call_llm(prompt)
        return {"mq_code": content}

    async def setup_api_gateway(self, routes: str) -> Dict[str, Any]:
        """配置 API 网关"""
        prompt = f"""
请配置 go-zero API 网关:

路由定义: {routes}

输出:
1. .api 文件定义
2. 网关配置 yaml
3. 路由转发到各微服务的映射
4. 统一鉴权中间件
5. 限流/熔断配置
6. 请求日志与链路追踪
"""
        content = await self.call_llm(prompt)
        return {"gateway_code": content}

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理微服务任务"""
        task_type = task.get("subtype", "design")
        description = task.get("description", "")

        if task_type == "design":
            result = await self.design_microservice(
                task.get("service_name", ""),
                description
            )
        elif task_type == "proto":
            result = await self.create_proto(
                task.get("service_name", ""),
                description
            )
        elif task_type == "rabbitmq":
            result = await self.setup_rabbitmq(description)
        elif task_type == "gateway":
            result = await self.setup_api_gateway(description)
        else:
            result = await self.design_microservice(description, description)

        return self.format_result(task, str(result), result)
