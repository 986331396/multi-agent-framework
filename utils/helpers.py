"""
工具函数模块
提供配置加载、日志初始化等公共工具函数
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载 JSON 配置文件

    支持环境变量替换，格式: ${ENV_VAR_NAME}

    Args:
        config_path: 配置文件路径（相对或绝对）

    Returns:
        解析后的配置字典
    """
    path = Path(config_path)

    if not path.exists():
        # 尝试从项目根目录查找
        root_path = Path(__file__).parent.parent / config_path
        if root_path.exists():
            path = root_path
        else:
            logging.warning(f"配置文件未找到: {config_path}")
            return {}

    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    return _resolve_env_vars(config)


def _resolve_env_vars(obj: Any) -> Any:
    """递归解析对象中的环境变量引用 (${VAR_NAME} 格式)"""
    import re

    if isinstance(obj, str):
        pattern = r'\$\{(\w+)\}'

        def replace_var(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))

        return re.sub(pattern, replace_var, obj)

    elif isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}

    elif isinstance(obj, list):
        return [_resolve_env_vars(item) for item in obj]

    return obj


def setup_logging(
    log_config: Dict[str, Any],
    root_logger: Optional[logging.Logger] = None,
) -> None:
    """
    初始化日志系统

    Args:
        log_config: 日志配置字典
            - level: 日志级别 (DEBUG/INFO/WARNING/ERROR)
            - format: 日志格式字符串
            - file: 可选的日志文件路径
        root_logger: 可选的根日志器实例
    """
    logger = root_logger or logging.getLogger()
    level_name = log_config.get("level", "INFO").upper()
    log_format = log_config.get(
        "format",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    log_file = log_config.get("file")

    logger.setLevel(getattr(logging, level_name, logging.INFO))

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)

    # 文件处理器（可选）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)


def format_json_output(data: Any, indent: int = 2) -> str:
    """将数据格式化为美观的 JSON 字符串"""
    return json.dumps(data, ensure_ascii=False, indent=indent)


def validate_task(task: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    验证任务字典格式是否有效

    Returns:
        (是否有效, 错误信息)
    """
    if not isinstance(task, dict):
        return False, "任务必须是字典类型"

    if "type" not in task:
        return False, "缺少必需字段: type"

    if "description" not in task:
        return False, "缺少必需字段: description"

    return True, None


def get_current_timestamp() -> str:
    """获取当前时间的格式化字符串"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_get(data: Dict, *keys, default=None):
    """
    安全地从嵌套字典中取值

    用法: safe_get(config, 'api', 'model', default='gpt-4')
    """
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return default
        else:
            return default
    return result


class Timer:
    """简单的计时器上下文管理器"""

    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time = None
        self.elapsed = 0

    def __enter__(self):
        import time
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        import time
        self.elapsed = time.time() - self.start_time
        logging.debug(f"[Timer] {self.name}: {self.elapsed:.3f}s")
