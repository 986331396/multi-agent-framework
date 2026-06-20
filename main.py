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

    # 预加载 UI 规格（供审核流程使用）
    ui_spec_path = Path("tasks/ui_specs/clothDiy_ui_specification.json")
    ui_spec_content = ""
    if ui_spec_path.exists():
        with open(ui_spec_path, "r", encoding="utf-8") as f:
            ui_spec_content = f.read()
        logger.info(f"已加载 UI 规格文档 ({len(ui_spec_content)} 字符)")

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

            # ===== 检查是否需要双 AI 审核流程 =====
            needs_review = task.get("needs_review", False)
            is_3d_page = task.get("is_3d_page", False)
            page_name = task.get("page_name", "")

            if needs_review:
                print(f"🔍 启用双 AI 审核模式 (UI审核 + 功能测试)")
                print(f"   3D页面: {'是' if is_3d_page else '否'}")
                print(f"{'=' * 60}")

                # 构建实现任务
                impl_task = {
                    "type": task.get("impl_type", "ui_page_3d_impl" if is_3d_page else "ui_page_impl"),
                    "description": task.get("description", ""),
                    "context": task.get("context", ""),
                    "page_name": page_name,
                    "screenshot_description": task.get("screenshot_description", ""),
                    "ui_file": task.get("ui_file", ""),
                    **task.get("extra_impl_params", {}),
                }

                # 指定实现 Agent（如果有）
                assigned_impl_agent = task.get("assigned_agent")

                if assigned_impl_agent:
                    impl_agent = coordinator.registered_agents.get(assigned_impl_agent)
                    if impl_agent:
                        # 先让实现 Agent 生成代码
                        print(f"\n[Phase 1] 实现阶段 - Agent: {assigned_impl_agent}")
                        impl_result = await impl_agent.execute_with_retry(impl_task)
                        generated_code = impl_result.get("content", "")
                    else:
                        print(f"⚠️ 未找到实现 Agent '{assigned_impl_agent}'，回退到自动路由")
                        generated_code = ""
                else:
                    generated_code = ""

                # 走完整审核流程
                if generated_code:
                    # 如果已经生成了代码，直接构建审核任务
                    review_result = await _run_review_pipeline(
                        coordinator, task, generated_code, ui_spec_content, page_name, is_3d_page
                    )
                    result = review_result
                else:
                    # 使用 Coordinator 的 process_with_review 方法
                    result = await coordinator.process_with_review(
                        impl_task=impl_task,
                        ui_spec=ui_spec_content,
                        page_name=page_name,
                        is_3d_page=is_3d_page,
                    )
            else:
                # 普通执行模式
                print(f"{'=' * 60}")

                exec_task = {
                    "type": task.get("type", "interactive"),
                    "description": task.get("description", ""),
                    "context": task.get("context", ""),
                    "module_name": task.get("module_name", ""),
                    "page_name": task.get("page_name", ""),
                }

                assigned = task.get("assigned_agent")
                if assigned:
                    print(f"指定 Agent: {assigned}")
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

            # 显示完成状态
            if needs_review:
                verdict = result.get("final_verdict", {})
                status_icon = {"PASS": "✅", "CONDITIONAL_PASS": "⚠️", "FAIL": "❌"}
                icon = status_icon.get(verdict.get("status", ""), "📋")
                score_info = verdict.get("scores", {})
                print(f"\n{icon} 审核完成: {verdict.get('message', '无判定')}")
                if score_info:
                    print(f"   分数: UI={score_info.get('ui_review', '?')} | 测试={score_info.get('func_test', '?')} | 综合={score_info.get('average', '?')}")
            else:
                status = result.get("status", "unknown") if isinstance(result, dict) else "unknown"
                icon = "✅" if status == "completed" else "❌"
                print(f"\n{icon} 任务完成: {task.get('name', task_id)}")

        remaining = next_remaining

    if remaining:
        print(f"\n⚠️ 以下任务因依赖未满足而跳过: {remaining}")

    return results


async def _run_review_pipeline(
    coordinator: Coordinator,
    original_task: dict,
    generated_code: str,
    ui_spec: str,
    page_name: str,
    is_3d_page: bool
) -> dict:
    """执行双 AI 审核 Pipeline"""
    import time
    start_time = time.time()

    pipeline_result = {
        "page_name": page_name,
        "is_3d_page": is_3d_page,
        "pipeline_status": "running",
        "phase_1_impl": {"status": "completed", "code_length": len(generated_code)},
        "phase_2_review": None,
        "phase_3_test": None,
        "final_verdict": None,
    }

    # Phase 2 & 3: 并行审核
    print(f"\n[Phase 2] 🎨 UI 还原度审核 (ReviewerAgent)...")
    print(f"[Phase 3] 🔧 功能测试审核 (TesterAgent)...")
    print(f"   → 两个审核 Agent 并行执行\n")

    review_task = {
        "id": f"review_{page_name}",
        "type": "ui_review",
        "description": f"审核 {page_name} 的 UI 还原度",
        "page_name": page_name,
        "ui_spec": ui_spec,
        "generated_code": generated_code,
        "screenshot_description": original_task.get("screenshot_description", ""),
    }

    test_task = {
        "id": f"test_{page_name}",
        "type": "func_test",
        "description": f"测试 {page_name} 的功能和代码质量",
        "page_name": page_name,
        "generated_code": generated_code,
        "requirements": original_task.get("description", ""),
        "is_3d_page": is_3d_page,
    }

    review_coro = coordinator.dispatch_task_to("ui_reviewer", review_task)
    test_coro = coordinator.dispatch_task_to("qa_tester", test_task)

    review_result, test_result = await asyncio.gather(
        review_coro, test_coro, return_exceptions=True
    )

    if isinstance(review_result, Exception):
        pipeline_result["phase_2_review"] = {"status": "error", "error": str(review_result)}
        print(f"   [UI审核] ❌ 异常: {review_result}")
    else:
        pipeline_result["phase_2_review"] = review_result
        print(f"   [UI审核] ✅ 完成")

    if isinstance(test_result, Exception):
        pipeline_result["phase_3_test"] = {"status": "error", "error": str(test_result)}
        print(f"   [功能测试] ❌ 异常: {test_result}")
    else:
        pipeline_result["phase_3_test"] = test_result
        print(f"   [功能测试] ✅ 完成")

    elapsed = time.time() - start_time
    pipeline_result["elapsed_seconds"] = round(elapsed, 1)

    # 分数提取（健壮版）
    def extract_score(r):
        if not isinstance(r, dict):
            return 0
        # 方法1：直接获取键（支持多种可能键名）
        for key in ["overall_score", "test_score", "score", "rating"]:
            v = r.get(key, None)
            if v is not None:
                try:
                    return int(v)
                except (ValueError, TypeError):
                    pass
        # 方法2：从 content 字段解析 JSON
        content = r.get("content", "")
        if content and isinstance(content, str):
            import json, re
            # 尝试直接解析 JSON
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    for key in ["overall_score", "test_score", "score"]:
                        v = parsed.get(key, None)
                        if v is not None:
                            return int(v)
            except (json.JSONDecodeError, ValueError):
                pass
            # 正则搜索各种格式
            patterns = [
                r'"(overall_score|test_score|score|rating)"\s*:\s*(\d+)',
                r'(总分|分数|score|rating)[:\s]*(\d+)',
            ]
            for pat in patterns:
                m = re.search(pat, content, re.IGNORECASE)
                if m:
                    return int(m.group(2))
        # 方法3：递归搜索嵌套字典
        def search_score(d, depth=0):
            if depth > 3 or not isinstance(d, dict):
                return None
            for k, v in d.items():
                if "score" in k.lower():
                    try:
                        return int(v)
                    except (ValueError, TypeError):
                        pass
                if isinstance(v, dict):
                    r = search_score(v, depth + 1)
                    if r is not None:
                        return r
            return None
        found = search_score(r)
        return found if found is not None else 0

    rv_score = extract_score(pipeline_result.get("phase_2_review", {}))
    tt_score = extract_score(pipeline_result.get("phase_3_test", {}))
    avg = (rv_score + tt_score) / 2 if (rv_score > 0 or tt_score > 0) else 0

    if avg >= 80 and rv_score >= 75 and tt_score >= 75:
        vs, vm = "PASS", f"通过 ✅ — UI({rv_score}) + 测试({tt_score}) = 综合({avg:.0f})"
    elif avg >= 60:
        vs, vm = "CONDITIONAL_PASS", f"有条件通过 ⚠️ — 需修复关键问题 (UI:{rv_score}, 测试:{tt_score})"
    else:
        vs, vm = "FAIL", f"不通过 ❌ — 需重新实现 (UI:{rv_score}, 测试:{tt_score})"

    pipeline_result.update({
        "pipeline_status": "completed",
        "final_verdict": {"status": vs, "message": vm, "scores": {"ui_review": rv_score, "func_test": tt_score, "average": round(avg, 1)}},
        "elapsed_seconds": round(elapsed, 1),
    })

    print(f"\n{'─' * 50}")
    print(f"  最终判定: {vm}")
    print(f"  总耗时: {elapsed:.1f}s")
    print(f"{'─' * 50}")

    return pipeline_result


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
