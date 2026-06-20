# Multi-Agent Framework

一个基于 Python 的多智能体协作框架，支持多个 AI Agent 协同工作完成复杂任务。

## 项目架构

```
multi-agent-framework/
├── README.md                 # 项目说明
├── main.py                   # 主入口文件
├── requirements.txt          # 依赖包
├── config/
│   └── config.json           # 全局配置
├── agents/
│   ├── base_agent.py         # Agent 基类
│   ├── coordinator.py        # 协调者 Agent
│   ├── research_agent.py     # 研究 Agent
│   └── coding_agent.py       # 编程 Agent
├── utils/
│   └── helpers.py            # 工具函数
├── tests/
│   └── test_agents.py        # 单元测试
└── docs/
    └── architecture.md       # 架构文档
```

## 核心特性

1. **模块化设计**: 每个 Agent 独立封装，可灵活扩展
2. **任务协调**: 通过 Coordinator 统一分配和调度任务
3. **消息传递**: Agent 之间通过标准化消息格式通信
4. **配置驱动**: 支持 JSON 配置文件动态调整参数
5. **错误处理**: 完善的异常处理和重试机制

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行框架

```bash
python main.py
```

## 配置说明

编辑 `config/config.json` 可以自定义：
- Agent 数量和类型
- API 密钥和端点
- 任务超时时间
- 日志级别

## Agent 类型

| Agent | 功能 |
|-------|------|
| Coordinator | 任务分解与调度 |
| ResearchAgent | 信息检索与分析 |
| CodingAgent | 代码生成与调试 |

## 技术栈

- Python 3.9+
- OpenAI API / 兼容接口
- JSON 配置
- 异步编程 (asyncio)

## License

MIT License
