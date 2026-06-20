"""
测试工程师 Agent
负责单元测试、集成测试、3D兼容性测试、性能压测
"""

from typing import Any, Dict

from ..base_agent import BaseAgent


class QAAgent(BaseAgent):
    """
    测试工程师 Agent

    专业领域: Go testing、API集成测试、3D兼容性、性能压测
    核心职责:
      1. Go 单元测试编写
      2. API 集成测试
      3. 3D 模型兼容性测试
      4. 70WDAU 性能压测方案
      5. 测试用例管理
    """

    async def write_unit_tests(self, module_name: str, code_summary: str) -> Dict[str, Any]:
        """编写单元测试"""
        prompt = f"""
请为模块「{module_name}」编写 Go 单元测试:

代码概要: {code_summary}

输出:
1. 完整的 _test.go 文件
2. Table-driven 测试用例
3. Mock 依赖（使用 gomock 或手写 mock）
4. 边界情况测试
5. 并发安全测试（如需要）
6. 测试覆盖率目标: 80%+
"""
        content = await self.call_llm(prompt)
        return {"test_code": content}

    async def write_api_tests(self, api_spec: str) -> Dict[str, Any]:
        """编写 API 集成测试"""
        prompt = f"""
请为以下 API 编写集成测试:

API 规格: {api_spec}

输出:
1. Go 集成测试代码（httptest）
2. 测试用例覆盖:
   - 正常流程
   - 参数校验失败
   - 权限不足
   - 资源不存在
   - 并发请求
3. 测试数据准备与清理
4. 测试数据库使用（SQLite 内存模式）
"""
        content = await self.call_llm(prompt)
        return {"api_tests": content}

    async def design_load_test(self, scenario: str) -> Dict[str, Any]:
        """设计性能压测方案"""
        prompt = f"""
请为「{scenario}」设计 70WDAU 性能压测方案:

输出:
1. 压测场景定义（首页/3D加载/下单/支付）
2. 压测工具选择（k6/Locust/wrk）
3. 压测脚本代码
4. 阶梯式加压策略
5. 关键指标与 SLA 定义:
   - P99 延迟 < 500ms
   - 错误率 < 0.1%
   - QPS 目标
6. 瓶颈分析框架
7. 扩容建议
"""
        content = await self.call_llm(prompt)
        return {"load_test": content}

    async def create_3d_compat_test(self) -> Dict[str, Any]:
        """创建3D兼容性测试方案"""
        prompt = f"""
请设计 3D 模型兼容性测试方案:

测试范围:
- 不同机型 WebGL 2.0 支持检测
- SMPL-X 模型加载成功率
- Draco 解码兼容性
- 渲染帧率基准
- 内存占用监控

输出:
1. 测试机型矩阵（iOS/Android 各档位）
2. 自动化测试脚本
3. 性能基准数据表
4. 降级策略触发条件
5. 监控埋点方案
"""
        content = await self.call_llm(prompt)
        return {"compat_test": content}

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理测试任务"""
        task_type = task.get("subtype", "unit_test")
        description = task.get("description", "")

        if task_type == "unit_test":
            result = await self.write_unit_tests(
                task.get("module_name", ""),
                description
            )
        elif task_type == "api_test":
            result = await self.write_api_tests(description)
        elif task_type == "load_test":
            result = await self.design_load_test(description)
        elif task_type == "3d_compat":
            result = await self.create_3d_compat_test()
        else:
            result = await self.write_unit_tests(description, description)

        return self.format_result(task, str(result), result)
