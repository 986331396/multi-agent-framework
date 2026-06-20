"""
Multi-Agent Framework - Agents Package
包含所有 Agent 类的定义和导出
"""

from .base_agent import BaseAgent
from .coordinator import Coordinator
from .research_agent import ResearchAgent
from .coding_agent import CodingAgent

__all__ = [
    "BaseAgent",
    "Coordinator",
    "ResearchAgent",
    "CodingAgent",
]
