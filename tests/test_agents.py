"""
Multi-Agent Framework 单元测试
测试所有 Agent 的核心功能
"""

import asyncio
import json
import os
import sys
import pytest

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from agents.coordinator import Coordinator
from agents.research_agent import ResearchAgent
from agents.coding_agent import CodingAgent


# 测试配置
TEST_CONFIG = {
    "version": "1.0.0-test",
    "agents": {
        "coordinator": {
            "name": "TestCoordinator",
            "role": "测试协调者",
            "description": "测试用协调者",
        },
        "researcher": {
            "name": "TestResearcher",
            "role": "测试研究员",
            "description": "测试用研究员",
        },
        "coder": {
            "name": "TestCoder",
            "role": "测试程序员",
            "description": "测试用程序员",
        },
    },
}


class TestBaseAgent:
    """BaseAgent 基类测试"""

    def test_agent_initialization(self):
        """测试 Agent 基本初始化"""
        agent = BaseAgent(TEST_CONFIG)
        assert agent.name == "BaseAgent"
        assert agent.role == "通用助手"

    def test_message_format(self):
        """测试消息格式化"""
        agent = BaseAgent(TEST_CONFIG)
        msg = agent.format_message("测试内容", {"key": "value"})
        assert msg["sender"] == "BaseAgent"
        assert msg["content"] == "测试内容"
        assert msg["metadata"]["key"] == "value"
        assert "timestamp" in msg

    def test_repr(self):
        """测试字符串表示"""
        agent = BaseAgent(TEST_CONFIG)
        repr_str = repr(agent)
        assert "BaseAgent" in repr_str

    @pytest.mark.asyncio
    async def test_execute_with_retry_success(self):
        """测试重试机制 - 成功情况"""
        class MockAgent(BaseAgent):
            async def process(self, task):
                return {"status": "ok"}

        agent = MockAgent(TEST_CONFIG)
        result = await agent.execute_with_retry({"type": "test"})
        assert result["status"] == "ok"


class TestResearchAgent:
    """ResearchAgent 测试"""

    @pytest.fixture
    def researcher(self):
        return ResearchAgent(TEST_CONFIG)

    def test_researcher_init(self, researcher):
        """测试研究 Agent 初始化"""
        assert researcher.name == "TestResearcher"
        assert researcher.role == "测试研究员"

    @pytest.mark.asyncio
    async def test_gather_information(self, researcher):
        """测试信息收集功能"""
        info = await researcher.gather_information("测试查询")
        assert "query" in info
        assert "sources" in info
        assert "key_findings" in info
        assert len(info["sources"]) > 0

    @pytest.mark.asyncio
    async def test_process_research_task(self, researcher):
        """测试完整研究流程"""
        task = {"id": "test_1", "type": "research", "description": "分析 AI 技术"}
        result = await researcher.process(task)

        assert result["status"] == "completed"
        assert result["agent"] == "TestResearcher"
        assert "summary" in result
        assert "report" in result
        assert len(result["recommendations"]) > 0


class TestCodingAgent:
    """CodingAgent 测试"""

    @pytest.fixture
    def coder(self):
        return CodingAgent(TEST_CONFIG)

    def test_coder_init(self, coder):
        """测试编程 Agent 初始化"""
        assert coder.name == "TestCoder"
        assert coder.role == "测试程序员"

    @pytest.mark.asyncio
    async def test_design_solution(self, coder):
        """测试方案设计"""
        solution = await coder.design_solution("构建 API 服务")
        assert "requirement" in solution
        assert "architecture" in solution
        assert "tech_stack" in solution
        assert len(solution["architecture"]["components"]) > 0

    @pytest.mark.asyncio
    async def test_process_coding_task(self, coder):
        """测试完整编程流程"""
        task = {"id": "code_1", "type": "coding", "description": "开发用户模块"}
        result = await coder.process(task)

        assert result["status"] == "completed"
        assert result["agent"] == "TestCoder"
        assert "solution" in result
        assert "code_structure" in result
        assert "code_review" in result


class TestCoordinator:
    """Coordinator 协调者测试"""

    @pytest.fixture
    def coordinator(self):
        return Coordinator(TEST_CONFIG)

    @pytest.fixture
    def setup_agents(self, coordinator):
        """设置带注册 Agent 的协调者"""
        researcher = ResearchAgent(TEST_CONFIG)
        coder = CodingAgent(TEST_CONFIG)
        coordinator.register_agent("researcher", researcher)
        coordinator.register_agent("coder", coder)
        return coordinator

    def test_coordinator_init(self, coordinator):
        """测试协调者初始化"""
        assert coordinator.name == "TestCoordinator"
        assert len(coordinator.registered_agents) == 0

    def test_register_agents(self, coordinator):
        """测试 Agent 注册"""
        researcher = ResearchAgent(TEST_CONFIG)
        coordinator.register_agent("researcher", researcher)
        assert "researcher" in coordinator.registered_agents

    @pytest.mark.asyncio
    async def test_decompose_task(self, coordinator):
        """测试任务分解"""
        task = {
            "type": "complex_task",
            "description": "综合开发任务",
            "priority": "high",
        }
        subtasks = await coordinator.decompose_task(task)
        assert len(subtasks) >= 2  # 至少分解为研究和编码任务

    @pytest.mark.asyncio
    async def test_full_workflow(self, setup_agents):
        """测试完整的协调工作流"""
        task = {
            "type": "complex_task",
            "description": "构建智能客服系统",
            "priority": "high",
        }

        result = await setup_agents.execute_with_retry(task)

        assert result["status"] == "completed"
        assert "details" in result
        assert len(result["details"]) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
