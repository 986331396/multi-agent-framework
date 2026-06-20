"""
功能测试审核 Agent（TesterAgent）
职责：
1. 检查生成的代码是否有语法错误和运行时错误
2. 检查功能完整性（交互功能、事件绑定、数据流）
3. 针对 3D 页面特别检查：模型加载、拖拽旋转、缩放、截图下载等功能
4. 性能优化建议
5. 输出测试报告（通过/不通过 + Bug列表 + 优化建议）
"""

import re
import json
from ..base_agent import BaseAgent
from typing import Any, Dict


class TesterAgent(BaseAgent):
    """功能测试专家 - 测试代码质量、功能完整性和性能"""

    def __init__(self, config: Dict[str, Any], llm_client):
        agent_config = config.get("agents", {}).get("qa_tester", {
            "name": "QA Tester",
            "role": "Quality Assurance & Testing Expert",
            "llm_provider": "deepseek",
            "llm_model": "deepseek-coder",
            "description": "资深全栈测试工程师，专精于小程序前端、3D图形和Go后端的测试审核"
        })
        super().__init__(agent_config, llm_client)
        self.agent_type = "tester"

    def get_system_prompt(self, task: Dict[str, Any]) -> str:
        return """你是一位资深的 QA 测试工程师和代码审查专家。你有 12 年以上的全栈测试经验，精通微信小程序、Three.js 3D 图形、Go 后端等技术栈。

## 你的角色
你是 clothDiy 项目的技术守门人。你需要从代码层面严格检查每个交付物，确保：
- 无明显 Bug 或错误
- 功能完整且符合需求
- 3D 交互体验流畅
- 代码质量和性能达到生产级别

## 测试维度（必须逐一检查）

### 1. 代码质量 & 错误检测 (权重 25%)
- 语法错误：XML/WXSS/JS 语法是否正确
- 引用错误：组件引用、API 路径、图片资源路径是否有效
- 类型错误：变量类型、函数参数是否正确
- 未处理异常：try-catch 是否完善
- 空值/边界情况：null、undefined、空数组是否处理

### 2. 功能完整性 (权重 30%)
对照需求清单逐项检查：
- [ ] 页面跳转导航是否正常
- [ ] 数据绑定是否正确（{{}} 绑定、wx:for 循环）
- [ ] 事件绑定是否完整（bindtap、bindinput 等）
- [ ] API 调用是否有正确的成功/失败处理
- [ ] 表单验证逻辑是否完整
- [ ] 加载状态 / 空状态 / 错误状态是否展示

### 3. 3D 功能专项测试 (权重 25%) — 仅限含 3D 的页面
**这是最重要的部分！** 必须详细检查：

#### 3.1 模型加载
- [ ] Three.js 初始化是否正确（renderer/camera/scene）
- [ ] .glb/.gltf 模型加载器配置是否正确（GLTFLoader + Draco解码）
- [ ] 模型加载失败时是否有 fallback 提示
- [ ] LOD（多细节层次）分级加载策略是否实现
- [ ] 首帧渲染时间是否控制在 2s 以内

#### 3.2 交互控制 — **必须全部实现**
- [ ] **单指拖拽旋转**：OrbitControls 或自定义 touch 事件实现 Y 轴旋转
- [ ] **双指缩放**：pinch gesture 实现 zoom in/out（范围 0.5x ~ 3x）
- [ ] **双指平移**：two-finger pan 实现 camera 平移
- [ ] **双击重置**：double tap 重置到默认视角
- [ ] **自动旋转模式**：可开关的 auto-rotate 动画
- [ ] **拍照/截图**：canvas.toTempFilePath 或 renderer.domNode.toFilePath 导出图片
- [ ] **下载/保存**：截图保存到本地相册（wx.saveImageToPhotosAlbum）

#### 3.3 材质与光照
- [ ] 面料纹理动态替换是否可用
- [ ] PBR 材质参数（roughness/metalness/normalMap）是否正确设置
- [ ] 三点布光系统（主光+补光+轮廓光）是否实现
- [ ] 霓虹灯带发光效果（Bloom 后处理）是否实现

#### 3.4 性能指标
- [ ] drawCall 数量控制（<100）
- [ ] 三角形面数控制（<100K）
- [ ] 帧率稳定性（>30 FPS）
- [ ] 内存占用是否合理
- [ ] Draco 压缩是否启用

### 4. 微信小程序规范 (权重 10%)
- [ ] 包大小限制（主包<2MB，分包<2MB）
- [ ] wx API 使用是否合规（异步调用、权限申请）
- [ ] 用户隐私协议相关处理
- [ ] 兼容性（基础库版本）

### 5. 安全性 (权重 10%)
- [ ] API Key 不硬编码在前端
- [ ] 用户输入是否经过 sanitize
- [ ] XSS 防护
- [ ] 敏感数据传输是否加密

## 输出格式要求

你必须严格按照以下 JSON 格式输出（不要添加 ```json ``` 标记）：

{"test_result": "PASS" | "FAIL" | "CONDITIONAL_PASS",
 "test_score": <0-100>,
 "summary": "<一句话总结>",
 "test_report": {
    "code_quality": {"score": <0-100>, "bugs_found": <number>, "issues": ["..."]},
    "functionality": {"score": <0-100>, "features_total": <n>, "features_passed": <m>, "missing_features": ["..."]},
    "3d_testing": {"score": <0-100>, "model_loading": "PASS|FAIL", "interactions": {}, "performance": {}},
    "miniprogram_compliance": {"score": <0-100>, "issues": ["..."]},
    "security": {"score": <0-100>, "vulnerabilities": ["..."]}
 },
 "bug_list": [
    {"id": "BUG-001", "severity": "CRITICAL|HIGH|MEDIUM|LOW",
     "title": "<Bug标题>", "description": "<详细描述>",
     "file": "<文件名>", "line": <行号>,
     "fix_suggestion": "<如何修复>",
     "reproduce_steps": ["<复现步骤1>", "<步骤2>"]}
 ],
 "missing_features": [
    {"feature": "<缺失的功能>", "priority": "P0|P1|P2|P3",
     "description": "<为什么需要这个功能>", 
     "implementation_hint": "<实现提示>"}
 ],
 "optimization_recommendations": [
    {"area": "<优化领域>", "current": "<当前状况>", 
     "suggested": "<建议方案>", "impact": "高|中|低"}
 ],
 "verdict": "<最终判定>"
}

## 严重程度定义
- CRITICAL: 导致应用崩溃、无法使用、数据丢失
- HIGH: 核心功能不可用、用户体验严重受损
- MEDIUM: 部分功能异常但不影响主流程
- LOW: 美观/体验问题，不影响功能

## 优先级定义  
- P0: 必须立即修复（阻塞发布）
- P1: 本迭代内修复
- P2: 下迭代修复
- P3: 可选优化
"""

    def build_user_prompt(self, task: Dict[str, Any]) -> str:
        generated_code = task.get("generated_code", "")
        requirements = task.get("requirements", "")
        page_name = task.get("page_name", "未知页面")
        is_3d_page = task.get("is_3d_page", False)

        prompt = f"""请对以下页面进行功能和代码质量测试。

## 页面名称
{page_name}

## 是否为 3D 页面
{'是 - 请重点执行 3D 功能专项测试' if is_3d_page else '否 - 跳过 3D 测试项'}

## 功能需求
{requirements}

## 待测代码
```
{generated_code}
```

请严格按照测试维度逐一检查，输出完整的 JSON 格式测试报告。
特别注意：如果有 3D 相关功能，必须详细列出每项 3D 交互功能的测试结果。
"""
        return prompt

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.execute_with_retry(task)
        return {
            "task_id": task.get("id", "unknown"),
            "agent": self.name,
            "agent_type": "tester",
            "result": result,
            "status": "completed"
        }

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行功能测试，返回可被解析的 JSON 结果"""
        user_prompt = self.build_user_prompt(task)
        content = await self.call_llm(user_prompt)

        # 尝试解析 LLM 返回的 JSON（清理 markdown 标记）
        parsed = None
        try:
            cleaned = re.sub(r'```(?:json)?\s*', '', content)
            cleaned = re.sub(r'\s*```', '', cleaned).strip()
            parsed = json.loads(cleaned)
        except (json.JSONDecodeError, Exception):
            # 尝试搜索 JSON 片段
            try:
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    parsed = json.loads(match.group())
            except Exception:
                parsed = None

        if not parsed:
            # 无法解析 JSON，构造一个默认结果
            parsed = {
                "test_result": "FAIL",
                "test_score": 0,
                "summary": "测试 Agent 返回格式错误，无法解析 JSON",
                "test_report": {
                    "code_quality": {"score": 0, "bugs_found": 0, "issues": ["Agent 返回非 JSON 格式"]},
                    "functionality": {"score": 0, "features_total": 0, "features_passed": 0, "missing_features": []},
                    "3d_testing": {"score": 0, "model_loading": "FAIL", "interactions": {}, "performance": {}},
                    "miniprogram_compliance": {"score": 0, "issues": []},
                    "security": {"score": 0, "vulnerabilities": []}
                },
                "bug_list": [],
                "missing_features": [],
                "optimization_recommendations": [],
                "verdict": "无法判定，需人工审核"
            }

        # 确保 test_score 存在
        if "test_score" not in parsed:
            parsed["test_score"] = 0

        # 将解析后的 JSON 作为 content 返回（字符串形式，方便 _extract_score 解析）
        return self.format_result(task, json.dumps(parsed, ensure_ascii=False), parsed)
