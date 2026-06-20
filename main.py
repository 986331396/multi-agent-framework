"""
Multi-Agent Framework - 主入口
多智能体协作框架的启动入口
支持多 LLM Provider（OpenAI/DeepSeek/Qwen/CodeBuddy）和专业化 Agent 团队

用法:
    python main.py                  # 演示模式（执行内置示例任务）
    python main.py --interactive    # 交互模式（逐条输入任务）
    python main.py --file tasks.json  # 文件模式（从 JSON 文件批量执行任务）
    python main.py --file tasks.md   # 也支持 Markdown 格式任务文件
"""

import asyncio
import json
import logging
import sys
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from agents.coordinator import Coordinator
from utils.helpers import setup_logging, load_config
from utils.llm_client import LLMClient

logger = logging.getLogger(__name__)


def load_tasks_from_file(file_path: str) -> list:
    """
    从文件加载任务列表
    支持 JSON 和 Markdown 两种格式

    JSON 格式: { "tasks": [ { "description": "...", ... }, ... ] }
    Markdown 格式: 每个 ## 标题为一个任务，正文为 description
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"任务文件不存在: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 支持两种 JSON 结构:
        # 1. { "tasks": [...] }
        # 2. [ ... ]  (直接是数组)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "tasks" in data:
            return data.get("tasks", [])
        else:
            raise ValueError("JSON 任务文件格式错误，需要是数组或含 tasks 字段的对象")

    elif suffix in (".md", ".markdown", ".txt"):
        # 解析 Markdown: ## 标题 为一个任务
        tasks = []
        current_task = None
        current_lines = []

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip()

                if line.startswith("## ") and not line.startswith("###"):
                    # 保存上一个任务
                    if current_task is not None:
                        current_task["description"] = "\n".join(current_lines).strip()
                        tasks.append(current_task)

                    # 新任务
                    name = line[3:].strip()
                    current_task = {
                        "name": name,
                        "type": "interactive",
                        "description": "",
                    }
                    current_lines = []

                elif line.startswith("### ") and current_task is not None:
                    # 子标题作为 context
                    if "context" not in current_task:
                        current_task["context"] = line[4:].strip()
                    current_lines.append(line)
                elif current_task is not None:
                    current_lines.append(line)

        # 保存最后一个任务
        if current_task is not None:
            current_task["description"] = "\n".join(current_lines).strip()
            tasks.append(current_task)

        return tasks

    else:
        raise ValueError(f"不支持的文件格式: {suffix}，请用 .json 或 .md")


async def run_tasks(tasks: list, coordinator: Coordinator, parallel: bool = False):
    """
    执行任务列表

    Args:
        tasks: 任务列表
        coordinator: 协调者实例
        parallel: 是否并行执行（默认串行，按 depends_on 可并行）
    """
    results = []
    completed_ids = set()

    # 构建依赖图
    id_map = {t.get("id", f"task_{i}"): t for i, t in enumerate(tasks)}

    remaining = list(range(len(tasks)))

    max_iter = len(tasks) * 2
    iteration = 0

    while remaining and iteration < max_iter:
        iteration += 1
        next_remaining = []

        for idx in remaining:
            task = tasks[idx]
            task_id = task.get("id", f"task_{idx}")

            # 检查依赖
            deps = task.get("depends_on", [])
            if deps and not all(d in completed_ids for d in deps):
                next_remaining.append(idx)
                continue

            # 执行任务
            print(f"\n{'=' * 60}")
            print(f"[任务 {idx + 1}/{len(tasks)}] {task.get('name', task_id)}")
            print(f"类型: {task.get('type', 'auto')}")
            print(f"{'=' * 60}")

            # 构建执行参数
            exec_task = {
                "type": task.get("type", "interactive"),
                "description": task.get("description", ""),
                "context": task.get("context", ""),
                "module_name": task.get("module_name", ""),
            }

            # 如果指定了 assigned_agent，直接执行
            assigned = task.get("assigned_agent")
            if assigned:
                print(f"指定 Agent: {assigned}")
                # 直接调用指定 Agent
                agent = coordinator.registered_agents.get(assigned)
                if agent:
                    result = await agent.execute(exec_task)
                else:
                    print(f"警告: 找不到 Agent '{assigned}'，使用自动路由")
                    result = await coordinator.execute(exec_task)
            else:
                result = await coordinator.execute(exec_task)

            results.append({
                "id": task_id,
                "name": task.get("name", task_id),
                "result": result,
            })

            completed_ids.add(task_id)
            print(f"\n✅ 任务完成: {task.get('name', task_id)}")

        remaining = next_remaining

    if remaining:
        print(f"\n⚠️ 以下任务因依赖未满足而跳过: {remaining}")

    return results


async def file_mode(file_path: str, parallel: bool = False):
    """文件模式：从文件加载任务并执行"""
    config = load_config("config/config.json")
    setup_logging(config.get("logging", {}))

    llm_client = LLMClient(config.get("llm_providers", {}))
    coordinator = Coordinator(config, llm_client)

    print("\n" + "=" * 60)
    print("Multi-Agent Framework - 文件执行模式")
    print("=" * 60)
    print(f"任务文件: {file_path}")
    print(f"已加载 {len(coordinator.list_agents())} 个专业 Agent")

    # 加载任务
    tasks = load_tasks_from_file(file_path)
    print(f"共 {len(tasks)} 个任务\n")

    if not tasks:
        print("⚠️ 文件中没有找到任务")
        return

    # 预览任务列表
    print("任务列表:")
    for i, t in enumerate(tasks):
        name = t.get("name", t.get("description", "")[:40])
        agent_hint = t.get("assigned_agent", "自动路由")
        print(f"  {i+1}. [{agent_hint}] {name}")
    print()

    # 执行任务
    results = await run_tasks(tasks, coordinator, parallel=parallel)

    # 输出汇总
    print("\n" + "=" * 60)
    print("执行汇总")
    print("=" * 60)
    for r in results:
        status = r["result"].get("status", "unknown")
        icon = "✅" if status == "completed" else "❌"
        print(f"  {icon} {r['name']} -> {status}")

    # 保存结果
    output_file = Path(file_path).stem + "_results.json"
    output_path = Path("outputs") / output_file
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n📁 结果已保存: {output_path}")


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
    parser = argparse.ArgumentParser(description="Multi-Agent Framework")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")
    parser.add_argument("--file", "-f", type=str, help="从文件加载任务（支持 .json / .md）")
    parser.add_argument("--parallel", "-p", action="store_true", help="并行执行任务（文件模式）")
    args = parser.parse_args()

    if args.file:
        asyncio.run(file_mode(args.file, parallel=args.parallel))
    elif args.interactive:
        asyncio.run(interactive_mode())
    else:
        asyncio.run(demo_multi_agent())
