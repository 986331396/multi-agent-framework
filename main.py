#!/usr/bin/env python3
"""
Multi-Agent Framework - 主入口
多智能体协作框架的启动入口，负责初始化配置、创建 Agent 实例并协调任务执行。
"""

import asyncio
import json
import logging
from typing import Dict, Any

from agents.coordinator import Coordinator
from agents.research_agent import ResearchAgent
from agents.coding_agent import CodingAgent
from utils.helpers import setup_logging, load_config

# 配置日志
logger = logging.getLogger(__name__)


async def main():
    """框架主函数"""
    # 加载配置
    config = load_config("config/config.json")

    # 初始化日志系统
    setup_logging(config.get("logging", {}))

    logger.info("=== Multi-Agent Framework 启动 ===")
    logger.info(f"加载配置: {config.get('version', 'unknown')}")

    # 创建 Agent 实例
    agents: Dict[str, Any] = {
        "coordinator": Coordinator(config),
        "researcher": ResearchAgent(config),
        "coder": CodingAgent(config),
    }

    # 注册 Agent 到协调者
    coordinator = agents["coordinator"]
    for name, agent in agents.items():
        if name != "coordinator":
            coordinator.register_agent(name, agent)
            logger.info(f"注册 Agent: {name}")

    # 示例任务
    task = {
        "type": "complex_task",
        "description": "分析问题并生成解决方案",
        "priority": "high",
    }

    # 执行任务
    try:
        result = await coordinator.execute(task)
        logger.info(f"任务完成: {result}")
        print("\n" + "=" * 50)
        print("执行结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("=" * 50 + "\n")
    except Exception as e:
        logger.error(f"任务执行失败: {e}", exc_info=True)
        raise

    logger.info("=== Multi-Agent Framework 结束 ===")


if __name__ == "__main__":
    asyncio.run(main())
