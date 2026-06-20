"""
工具函数模块
提供配置加载、日志初始化等公共工具
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict


def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载 JSON 配置文件

    Args:
        config_path: 配置文件相对或绝对路径

    Returns:
        配置字典，文件不存在时返回空字典
    """
    path = Path(config_path)

    if not path.exists():
        # 尝试从项目根目录查找
        root_path = Path(__file__).parent.parent / config_path
        if root_path.exists():
            path = root_path
        else:
            print(f"警告: 配置文件未找到: {config_path}")
            return {}

    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 支持环境变量替换（${VAR_NAME} 格式）
    config = _resolve_env_vars(config)

    return config


def _resolve_env_vars(obj: Any) -> Any:
    """递归解析对象中的环境变量引用"""
    if isinstance(obj, str):
        import re
        pattern = r'\$\{(\w+)\}'

        def replace_var(match):
            var_name = match.group(1)
            value = os.environ.get(var_name, match.group(0))
            return value

        return re.sub(pattern, replace_var, obj)
    elif isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_env_vars(item) for item in obj]
    return obj


def setup_logging(logging_config: Dict[str, Any]) -> None:
    """
    初始化日志系统

    Args:
        logging_config: 日志配置字典，包含 level, format, file 等
    """
    level = logging_config.get("level", "INFO").upper()
    log_format = logging_config.get(
        "format",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    log_file = logging_config.get("file")

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        handlers.append(file_handler)

    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format=log_format,
        handlers=handlers,
    )


def format_output(data: Dict[str, Any], indent: int = 2) -> str:
    """格式化输出为美观的 JSON 字符串"""
    return json.dumps(data, ensure_ascii=False, indent=indent)


def validate_task(task: Dict[str, Any]) -> bool:
    """验证任务格式是否有效"""
    required_fields = ["type", "description"]
    return all(field in task for field in required_fields)


def get_timestamp() -> str:
    """获取当前时间戳字符串"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
