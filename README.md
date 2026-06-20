# Multi-Agent Framework

一个支持**多 LLM Provider** 的多智能体协作框架，专为 clothDiy 服装DIY定制小程序项目设计。

## 核心特性

- 🔌 **多 LLM Provider 支持**: OpenAI、DeepSeek、通义千问、CodeBuddy，每个 Agent 可独立配置模型
- 🤖 **12 个专业化 Agent**: 产品经理、UI设计师、小程序前端、管理后台前端、3D图形工程师、Go后端、微服务、数据库、DevOps、3D建模师、供应链专家、测试工程师
- 🧠 **智能任务路由**: 根据任务类型自动分配给合适的 Agent，支持 LLM 辅助路由
- ⚡ **异步并发执行**: 多个 Agent 并行处理子任务
- 🔄 **自动重试机制**: 指数退避重试，提高可靠性
- ⚙️ **配置驱动**: JSON 配置 + 环境变量，灵活切换 Provider/Model

## 项目架构

```
multi-agent-framework/
├── main.py                        # 主入口（演示 + 交互 + 文件模式）
├── .env                           # API Key 配置（不提交Git）✅
├── .env.example                   # API Key 模板
├── config/
│   └── config.json                # 全局配置（多 Provider + Agent 定义）
├── tasks/                         # 任务文件目录 ✅
│   ├── clothdiy_tasks.json       # JSON 格式任务列表
│   └── clothdiy_tasks.md        # Markdown 格式任务列表
├── outputs/                       # 执行结果输出目录 ✅
├── agents/
│   ├── base_agent.py              # Agent 基类（含 LLM 调用）
│   ├── coordinator.py             # 协调者（任务分解+路由+整合）
│   └── specialists/               # 12个专业化 Agent
│       ├── product_agent.py       # 产品经理
│       ├── ui_ux_agent.py         # UI/UX设计师
│       ├── miniprogram_agent.py   # 小程序前端工程师
│       ├── admin_frontend_agent.py# 管理后台前端工程师
│       ├── three_graphics_agent.py# 3D图形工程师
│       ├── go_backend_agent.py    # Go后端工程师
│       ├── microservice_agent.py  # 微服务工程师
│       ├── database_agent.py      # 数据库工程师
│       ├── devops_agent.py        # DevOps工程师
│       ├── garment_modeling_agent.py  # 服装3D建模师
│       ├── supply_chain_agent.py  # 供应链专家
│       └── qa_agent.py            # 测试工程师
├── utils/
│   ├── helpers.py                 # 工具函数（含 .env 自动加载）
│   └── llm_client.py             # 多 Provider LLM 客户端
├── tests/
│   └── test_agents.py            # 单元测试
├── docs/
│   └── architecture.md           # 架构文档
└── requirements.txt
```

## 多 Provider 配置

`config/config.json` 支持配置多个 LLM Provider，每个 Agent 可独立指定使用的 Provider 和 Model:

```json
{
  "llm_providers": {
    "deepseek": {
      "provider": "deepseek",
      "base_url": "https://api.deepseek.com/v1",
      "api_key": "${DEEPSEEK_API_KEY}",
      "models": {
        "deepseek-chat": { "max_tokens": 8192, "temperature": 0.7 },
        "deepseek-coder": { "max_tokens": 8192, "temperature": 0.1 }
      }
    },
    "openai": {
      "provider": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key": "${OPENAI_API_KEY}",
      "models": {
        "gpt-4o": { "max_tokens": 4096, "temperature": 0.7 }
      }
    }
  },
  "agents": {
    "go_backend_dev": {
      "name": "GoBackendAgent",
      "llm_provider": "deepseek",
      "llm_model": "deepseek-coder",
      "system_prompt": "你是Go后端开发专家..."
    },
    "product_manager": {
      "name": "ProductAgent",
      "llm_provider": "deepseek",
      "llm_model": "deepseek-chat",
      "system_prompt": "你是资深产品经理..."
    }
  }
}
```

### 支持的 Provider

| Provider | Base URL | 推荐模型 |
|----------|----------|----------|
| DeepSeek | `https://api.deepseek.com/v1` | deepseek-chat, deepseek-coder, deepseek-reasoner |
| OpenAI | `https://api.openai.com/v1` | gpt-4o, gpt-4o-mini |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | qwen-max, qwen-plus |
| CodeBuddy | `https://api.codebuddy.cn/v1` | codebuddy-claude |

### 环境变量配置

```bash
# DeepSeek
export DEEPSEEK_API_KEY="sk-your-deepseek-key"

# OpenAI
export OPENAI_API_KEY="sk-your-openai-key"

# 通义千问
export DASHSCOPE_API_KEY="sk-your-qwen-key"

# CodeBuddy
export CODEBUDDY_API_KEY="ck-your-codebuddy-key"
```

## Agent 团队

为 clothDiy 项目定制的 12 个专业化 Agent:

| Agent Key | 角色 | 推荐模型 | 职责 |
|-----------|------|----------|------|
| `product_manager` | 产品经理 | deepseek-chat | 需求分析、PRD、用户故事、交互流程 |
| `ui_designer` | UI/UX设计师 | deepseek-chat | 界面设计、设计系统、配色方案 |
| `miniprogram_dev` | 小程序前端工程师 | deepseek-coder | 微信小程序开发、Three.js适配 |
| `admin_frontend_dev` | 管理后台前端工程师 | deepseek-coder | Vue3 + Ant Design 后台开发 |
| `three_graphics_eng` | 3D图形工程师 | deepseek-coder | SMPL-X变形、MorphTargets、Draco压缩 |
| `go_backend_dev` | Go后端工程师 | deepseek-coder | Gin + GORM + RESTful API |
| `microservice_dev` | 微服务工程师 | deepseek-coder | go-zero、gRPC、RabbitMQ |
| `database_eng` | 数据库工程师 | deepseek-coder | PostgreSQL、Elasticsearch、Redis |
| `devops_eng` | DevOps工程师 | deepseek-coder | Docker、K8s、CI/CD、监控 |
| `garment_modeling` | 服装3D建模师 | deepseek-chat | Blender建模、蒙皮绑定、glTF导出 |
| `supply_chain_expert` | 供应链专家 | deepseek-chat | 工厂撮合、订单状态机、工艺单 |
| `qa_engineer` | 测试工程师 | deepseek-coder | 单元测试、集成测试、性能压测 |

## 快速开始

### 1. 安装依赖

```bash
cd ~/Desktop/ai-project/multi-agent-framework
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `.env` 文件，填入你的 API Key（文件已创建）：
```bash
# .env 文件已创建，直接编辑即可
open .env   # macOS 打开编辑
# 或直接用 vim/nano 编辑
```

### 3. 运行方式

#### 方式一：演示模式（自动执行内置示例）
```bash
python main.py
```

#### 方式二：交互模式（逐条输入任务）
```bash
python main.py --interactive
```
进入后输入任务描述即可，输入 `quit` 退出：
```
📝 请输入任务: 帮我设计一个用户登录页面
📝 请输入任务: 写一个 Go 的订单 API 接口
📝 请输入任务: quit
```

#### 方式三：文件模式（从文件批量执行任务）✅ 推荐
```bash
# JSON 格式任务文件
python main.py --file tasks/clothdiy_tasks.json

# Markdown 格式任务文件
python main.py --file tasks/clothdiy_tasks.md

# 并行执行（实验性）
python main.py --file tasks/clothdiy_tasks.json --parallel
```

执行结果自动保存到 `outputs/` 目录。

---

## 任务文件格式

支持 **JSON** 和 **Markdown** 两种格式。

### JSON 格式（推荐）

```json
{
  "meta": { "project": "xxx", "description": "..." },
  "tasks": [
    {
      "id": "t001",
      "name": "用户登录模块",
      "type": "new_module",
      "description": "设计用户登录模块的需求规格...",
      "assigned_agent": "product_manager",
      "context": "项目上下文信息",
      "depends_on": ["t000"]
    }
  ]
}
```

**字段说明：**

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 否 | 任务 ID，用于 `depends_on` 依赖引用 |
| `name` | 否 | 任务名称（显示用） |
| `type` | 推荐 | 任务类型，影响自动路由（如 `new_module`/`api_spec`/`smplx_mapping`） |
| `description` | **是** | 任务详细描述 |
| `assigned_agent` | 否 | 指定 Agent（如 `go_backend_dev`），不填则自动路由 |
| `context` | 否 | 项目上下文，会注入给 LLM |
| `depends_on` | 否 | 依赖的任务 ID 列表，确保按顺序执行 |
| `module_name` / `page_name` 等 | 否 | 根据 `type` 可选的补充字段 |

### Markdown 格式

用 `##` 标题分隔每个任务，`###` 作为子标题：

```markdown
# 项目任务清单

## 用户登录模块 - 需求分析
### 背景
项目是服装DIY小程序...
### 需求描述
设计用户登录模块...
### 指定 Agent
product_manager

## 用户登录模块 - 数据库设计
...
```

---

## 任务路由规则

框架根据 `type` 字段自动路由到合适的 Agent：

| type | 路由到 |
|------|---------|
| `new_module` | 产品经理 + 数据库 + 后端 + 测试 |
| `api_spec` | 产品经理 + 后端 |
| `miniprogram_page` | 小程序前端工程师 |
| `admin_view` | 管理后台前端工程师 |
| `smplx_mapping` | 3D图形工程师 |
| `dockerfile` | DevOps工程师 |
| `blender_script` | 服装3D建模师 |
| `microservice_design` | 微服务工程师 |
| ... | 详见 `agents/coordinator.py` TASK_ROUTING_RULES |

## License

MIT License
