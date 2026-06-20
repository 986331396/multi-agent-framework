"""
DevOps工程师 Agent
负责 Docker、K8s、CI/CD、CDN、监控告警
"""

from typing import Any, Dict

from ..base_agent import BaseAgent


class DevOpsAgent(BaseAgent):
    """
    DevOps工程师 Agent

    专业领域: Docker、Kubernetes、GitHub Actions、CDN、Prometheus
    核心职责:
      1. Docker 容器化与 docker-compose 编排
      2. Kubernetes 部署清单
      3. CI/CD 流水线设计
      4. CDN 加速与对象存储配置
      5. 监控告警体系搭建
    """

    async def create_dockerfile(self, service_name: str, tech_stack: str) -> Dict[str, Any]:
        """创建 Dockerfile"""
        prompt = f"""
请为服务「{service_name}」创建 Dockerfile:

技术栈: {tech_stack}

输出:
1. 多阶段构建 Dockerfile
2. .dockerignore 文件
3. 镜像优化说明（层缓存/体积缩减）
4. 安全加固建议
"""
        content = await self.call_llm(prompt)
        return {"dockerfile": content}

    async def create_docker_compose(self, services: str) -> Dict[str, Any]:
        """创建 docker-compose 编排"""
        prompt = f"""
请创建 docker-compose.yml 编排以下服务:

服务列表: {services}

输出:
1. 完整的 docker-compose.yml
2. 各服务依赖关系
3. 数据卷挂载
4. 网络配置
5. 环境变量配置
6. 健康检查配置
7. 启动顺序控制
"""
        content = await self.call_llm(prompt)
        return {"compose": content}

    async def create_k8s_manifests(self, service_name: str, config: str) -> Dict[str, Any]:
        """创建 K8s 部署清单"""
        prompt = f"""
请为服务「{service_name}」创建 Kubernetes 部署清单:

配置: {config}

输出:
1. Deployment YAML
2. Service YAML
3. ConfigMap YAML
4. Secret YAML（模板）
5. Ingress YAML
6. HPA (水平自动伸缩) YAML
7. 滚动更新策略
"""
        content = await self.call_llm(prompt)
        return {"k8s": content}

    async def create_cicd_pipeline(self, project_name: str, stack: str) -> Dict[str, Any]:
        """创建 CI/CD 流水线"""
        prompt = f"""
请为项目「{project_name}」创建 GitHub Actions CI/CD 流水线:

技术栈: {stack}

输出:
1. .github/workflows/ci.yml - 持续集成
2. .github/workflows/cd.yml - 持续部署
3. 构建阶段（lint/test/build）
4. Docker 镜像推送
5. K8s 部署步骤
6. 通知配置（飞书/钉钉 Webhook）
7. 环境变量管理
"""
        content = await self.call_llm(prompt)
        return {"cicd": content}

    async def setup_monitoring(self, services: str) -> Dict[str, Any]:
        """搭建监控告警体系"""
        prompt = f"""
请为以下服务搭建监控告警体系:

服务: {services}

输出:
1. Prometheus 配置（scrape targets）
2. Grafana Dashboard JSON 模板
3. 告警规则（Alertmanager）
4. Sentry 错误监控集成
5. 日志收集方案（ELK/Loki）
6. 关键指标定义（API延迟/错误率/QPS）
7. 告警通知渠道配置
"""
        content = await self.call_llm(prompt)
        return {"monitoring": content}

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理 DevOps 任务"""
        task_type = task.get("subtype", "dockerfile")
        description = task.get("description", "")

        if task_type == "dockerfile":
            result = await self.create_dockerfile(
                task.get("service_name", ""),
                description
            )
        elif task_type == "compose":
            result = await self.create_docker_compose(description)
        elif task_type == "k8s":
            result = await self.create_k8s_manifests(
                task.get("service_name", ""),
                description
            )
        elif task_type == "cicd":
            result = await self.create_cicd_pipeline(
                task.get("project_name", ""),
                description
            )
        elif task_type == "monitoring":
            result = await self.setup_monitoring(description)
        else:
            result = await self.create_dockerfile(description, description)

        return self.format_result(task, str(result), result)
