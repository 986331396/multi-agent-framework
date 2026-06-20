# Multi-Agent Framework 架构文档

## 概述

Multi-Agent Framework 是一个基于 Python 的多智能体协作框架，采用**协调者模式（Coordinator Pattern）**实现多个 AI Agent 之间的协同工作。

## 核心架构

```
┌─────────────────────────────────────────────────────┐
│                   Main Entry (main.py)               │
│                  框架启动与配置加载                    │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              Coordinator (协调者 Agent)                │
│  ┌───────────┬──────────┬───────────────────┐       │
│  │ 任务分解   │ 任务分发  │    结果整合        │       │
│  └───────────┴──────────┴───────────────────┘       │
└───────┬───────────────┬───────────────┬─────────────┘
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ ResearchAgent│ │ CodingAgent  │  (可扩展...)    │
│  (研究专家)   │ │ (编程专家)   │               │
│              │ │              │               │
│ · 信息收集   │ · 方案设计    │               │
│ · 数据分析   │ · 代码生成    │               │
│ · 报告生成   │ · 代码审查    │               │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 组件说明

### 1. BaseAgent (基类)

所有 Agent 的抽象基类，定义了统一的接口：

| 方法 | 说明 |
|------|------|
| `process(task)` | 处理任务的核心方法（抽象） |
| `execute_with_retry()` | 带重试机制的任务执行 |
| `format_message()` | 标准化消息格式 |

### 2. Coordinator (协调者)

框架的核心调度组件：

- **任务分解**: 将复杂任务拆分为子任务
- **任务分发**: 将子任务分配给合适的 Agent
- **结果整合**: 汇总所有子任务结果生成最终输出
- **并发执行**: 使用 asyncio.gather 并行处理子任务

### 3. ResearchAgent (研究专家)

负责信息收集和分析工作流：

```
输入任务 → 信息收集(gather_information)
         → 数据分析(analyze_data)
         → 报告生成(generate_report)
         → 输出结构化研究结果
```

### 4. CodingAgent (编程专家)

负责技术开发工作流：

```
输入任务 → 方案设计(design_solution)
         → 代码生成(generate_code)
         → 代码审查(review_and_optimize)
         → 输出技术方案和代码骨架
```

## 数据流转

```
用户请求
    │
    ▼
[Task] ──→ Coordinator.decompose_task()
                    │
            ┌───────┴───────┐
            ▼               ▼
     ResearchAgent    CodingAgent
            │               │
            ▼               ▼
     [研究结果]      [技术方案]
            │               │
            └───────┬───────┘
                    ▼
          Coordinator.integrate_results()
                    │
                    ▼
             [最终整合报告]
```

## 消息格式

Agent 之间通过标准化消息进行通信：

```json
{
  "sender": "Agent 名称",
  "content": "消息内容",
  "metadata": {},
  "timestamp": "ISO 8601 格式时间戳"
}
```

## 配置系统

配置文件 (`config/config.json`) 支持以下层级：

```json
{
  "version": "版本号",
  "api": {
    "provider": "API 提供商",
    "model": "使用的模型"
  },
  "agents": {
    "agent_name": { ... }
  },
  "task_settings": {
    "timeout": "超时时间(秒)",
    "max_retries": "最大重试次数"
  }
}
```

支持环境变量替换：`${ENV_VAR_NAME}`

## 扩展指南

### 添加新的 Agent

1. 创建新文件 `agents/your_agent.py`
2. 继承 `BaseAgent` 类
3. 实现 `process()` 方法
4. 在 `config.json` 中添加配置
5. 在 `coordinator.py` 中注册

示例：

```python
from .base_agent import BaseAgent

class YourAgent(BaseAgent):
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # 实现你的逻辑
        return {"status": "completed", ...}
```

## 错误处理机制

- **重试机制**: 默认最多重试 3 次，指数退避
- **异常隔离**: 单个 Agent 失败不影响其他 Agent
- **超时控制**: 支持任务级别超时设置
- **日志追踪**: 完整的执行链路日志

## 性能考虑

- 所有 I/O 操作使用 async/await
- 子任务并发执行 (asyncio.gather)
- 结果缓存避免重复计算
- 连接池管理外部 API 调用
