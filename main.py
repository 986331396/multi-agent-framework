"""
Multi-Agent Framework - 主入口
多智能体协作框架的启动入口
支持多 LLM Provider（OpenAI/DeepSeek/Qwen/CodeBuddy）和专业化 Agent 团队
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from agents.coordinator import Coordinator
from utils.helpers import setup_logging, load_config
from utils.llm_client import LLMClient

logger = logging.getLogger(__name__)


async def demo_multi_agent():
    """演示多 Agent 协作"""

    # 加载配置
    config = load_config("config/config.json")

    # 初始化日志
    setup_logging(config.get("logging", {}))

    logger.info("=" * 60)
    logger.info("Multi-Agent Framework v2.0 启动")
    logger.info("=" * 60)

    # 创建 LLM 客户端（支持多 Provider）
    llm_client = LLMClient(config.get("llm_providers", {}))
    logger.info(f"已注册 LLM Provider: {llm_client.list_providers()}")
    logger.info(f"可用模型: {llm_client.list_models()}")

    # 创建协调者（自动注册所有 Agent）
    coordinator = Coordinator(config, llm_client)

    # 打印已注册的 Agent 团队
    agents = coordinator.list_agents()
    logger.info(f"\n已注册 {len(agents)} 个专业 Agent:")
    for a in agents:
        logger.info(f"  - {a['key']}: {a['name']} ({a['role']}) [{a['llm']}]")

    # === 示例任务 1: 创建新 API 模块（多 Agent 协作）===
    print("\n" + "=" * 60)
    print("示例任务: 创建「订单管理」API 模块")
    print("=" * 60)

    task = {
        "type": "new_module",
        "subtype": "new_module",
        "description": "创建订单管理模块，包含用户下单、工厂报价、订单状态流转、生产进度跟踪",
        "module_name": "order",
        "context": "服装DIY定制小程序 - 订单管理子系统",
    }

    result = await coordinator.execute(task)
    print("\n执行结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

    # === 示例任务 2: 3D 体型变形（单 Agent 精细化）===
    print("\n" + "=" * 60)
    print("示例任务: 实现 SMPL-X 体型参数映射")
    print("=" * 60)

    task2 = {
        "type": "smplx_mapping",
        "subtype": "smplx_mapping",
        "description": "实现厘米级体型参数到SMPL-X β参数的映射函数，包含10个维度",
    }

    result2 = await coordinator.execute(task2)
    print("\n执行结果:")
    print(json.dumps(result2, ensure_ascii=False, indent=2, default=str))

    logger.info("=" * 60)
    logger.info("Multi-Agent Framework 执行完毕")
    logger.info("=" * 60)


async def interactive_mode():
    """交互式模式：用户输入任务，框架自动分解并执行"""
    config = load_config("config/config.json")
    setup_logging(config.get("logging", {}))

    llm_client = LLMClient(config.get("llm_providers", {}))
    coordinator = Coordinator(config, llm_client)

    print("\n" + "=" * 60)
    print("Multi-Agent Framework - 交互模式")
    print("=" * 60)
    print(f"已加载 {len(coordinator.list_agents())} 个专业 Agent")
    print("输入任务描述，框架会自动分解并分配给合适的 Agent")
    print("输入 'quit' 退出\n")

    while True:
        user_input = input("📝 请输入任务: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue

        task = {
            "type": "interactive",
            "description": user_input,
        }

        print("\n⏳ 执行中...\n")
        result = await coordinator.execute(task)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(demo_multi_agent())
