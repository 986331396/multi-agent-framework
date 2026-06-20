"""
UI 还原度审核 Agent（ReviewerAgent）
职责：
1. 对比生成的页面代码与 UI 设计规格，检查还原度
2. 检查布局、颜色、字体、间距、组件是否匹配设计稿
3. 检查响应式适配是否正确
4. 输出审核报告（通过/不通过 + 详细问题列表）
"""

import re
import json
from ..base_agent import BaseAgent
from typing import Any, Dict


class ReviewerAgent(BaseAgent):
    """UI 还原度审核专家 - 审核前端代码与设计稿的一致性"""
    
    def __init__(self, config: Dict[str, Any], llm_client):
        agent_config = config.get("agents", {}).get("ui_reviewer", {
            "name": "UI Reviewer",
            "role": "UI/UX Design Review Expert",
            "llm_provider": "deepseek",
            "llm_model": "deepseek-chat",
            "description": "资深UI设计师，专精于对比设计稿与实现代码的还原度审核"
        })
        super().__init__(agent_config, llm_client)
        self.agent_type = "reviewer"

    def get_system_prompt(self, task: Dict[str, Any]) -> str:
        return """你是一位资深的 UI/UX 审核专家。你的任务是严格审核前端页面的 UI 还原度。

## 你的角色
你拥有 15 年以上的 UI/UX 设计和前端开发经验，能够精确识别设计与实现的差异。
你的审美标准极高，对像素级还原有强迫症般的要求。

## 审核维度（必须逐一检查）

### 1. 布局还原度 (权重 30%)
- 页面整体区域划分是否与设计稿一致
- 各模块的位置、大小比例是否正确
- 元素之间的间距（margin/padding）是否符合规格
- 是否有错位、重叠或溢出

### 2. 颜色还原度 (权重 25%)
- 背景色是否正确（主背景 #0a0a0f、卡片背景 #1a1a2e 等）
- 文字颜色是否正确（主文字 #fff、次要文字 #8b8b9e）
- 强调色是否使用得当（紫色 #7c3aed 作为主色调）
- 渐变效果是否与设计稿一致

### 3. 字体排版 (权重 15%)
- 字号是否与规格一致（标题 18-22px、正文 14px、辅助文字 12px）
- 字重是否正确（标题 700/600、正文 400）
- 行高是否合理
- 中英文混排是否协调

### 4. 组件样式 (权重 20%)
- 按钮：圆角(12px)、填充紫色(#7c3aed)、描边按钮样式
- 卡片：圆角(12-14px)、背景(#1a1a2e)、阴影
- 输入框：高度(42px)、背景色、placeholder 样式
- TabBar：高度(56px)、图标+文字布局、激活态颜色
- Badge/Tag：胶囊形状、尺寸、颜色

### 5. 3D 视窗区域 (权重 10% - 仅限动态试穿等含3D的页面)
- Canvas 区域占比是否正确
- 工具栏位置和样式（左侧工具栏 / 右侧操作栏）
- 浮动按钮的大小、图标、间距
- 霓虹光效/粒子背景是否实现

## 输出格式要求

你必须严格按照以下 JSON 格式输出（不要添加 ```json``` 标记）：

{{"overall_status": "PASS" | "FAIL" | "CONDITIONAL_PASS",
  "overall_score": <0-100>,
  "summary": "<一段话总结>",
  "details": {{
      "layout": {{"score": <0-100>, "status": "PASS|FAIL", "issues": ["..."]}},
      "color": {{"score": <0-100>, "status": "PASS|FAIL", "issues": ["..."]}},
      "typography": {{"score": <0-100>, "status": "PASS|FAIL", "issues": ["..."]}},
      "components": {{"score": <0-100>, "status": "PASS|FAIL", "issues": ["..."]}},
      "3d_viewport": {{"score": <0-100>, "status": "PASS|FAIL|N/A", "issues": ["..."]}}
  }},
  "critical_issues": [
      {{"severity": "CRITICAL|MAJOR|MINOR", "category": "<类别>", 
        "description": "<问题描述>", "suggestion": "<修复建议>"}}
  ],
  "optimization_suggestions": ["<优化建议>"],
  "verdict": "<最终结论：建议通过/需要修改后重审/必须重做>"
}}

## 评判标准
- 总分 >= 85: PASS（通过）
- 总分 70-84: CONDITIONAL_PASS（有条件通过，需修复 MAJOR 以上问题后上线）
- 总分 < 70: FAIL（不通过，需重新实现）

## 特别注意
- 这是 clothDiy 服装DIY定制项目，暗黑赛博朋克风格
- 所有页面均为微信小程序端（WeChat Mini Program）
- 使用 VantWeapp 组件库作为基础组件
- 3D 部分使用 Three.js 小程序适配版
"""

    def build_user_prompt(self, task: Dict[str, Any]) -> str:
        ui_spec = task.get("ui_spec", "")
        generated_code = task.get("generated_code", "")
        screenshot_desc = task.get("screenshot_description", "")
        page_name = task.get("page_name", "未知页面")
        
        return f"""请对以下页面进行 UI 还原度审核。

## 页面名称
{page_name}

## UI 设计规格说明
{ui_spec}

## 已生成的代码
```html/wxml/css/wxss/js
{generated_code}
```

## 设计稿截图描述
{screenshot_desc}

请严格按照审核维度逐一检查，输出完整的 JSON 格式审核报告。不要遗漏任何细节。
如果某个维度没有问题，也要明确标注 PASS 并给出理由。
"""

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.execute_with_retry(task)
        return {
            "task_id": task.get("id", "unknown"),
            "agent": self.name,
            "agent_type": "reviewer",
            "result": result,
            "status": "completed"
        }

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行 UI 还原度审核，返回可被解析的 JSON 结果"""
        user_prompt = self.build_user_prompt(task)
        content = await self.call_llm(user_prompt)

        # 增强 JSON 解析：支持多种格式
        parsed = None

        # 方法1：直接解析整个内容（假设 LLM 返回了纯 JSON）
        try:
            cleaned = re.sub(r'```(?:json)?\s*', '', content)
            cleaned = re.sub(r'\s*```', '', cleaned).strip()
            parsed = json.loads(cleaned)
        except (json.JSONDecodeError, Exception):
            pass

        # 方法2：搜索 JSON 对象（可能嵌入在解释性文字中）
        if not parsed:
            # 找到第一个 { 和最后一个 } 之间的内容
            try:
                start = content.index('{')
                end = content.rindex('}') + 1
                json_str = content[start:end]
                parsed = json.loads(json_str)
            except (ValueError, json.JSONDecodeError):
                pass

        # 方法3：逐字符搜索可解析的 JSON 片段
        if not parsed:
            try:
                depth = 0
                for i, ch in enumerate(content):
                    if ch == '{':
                        if depth == 0:
                            start = i
                        depth += 1
                    elif ch == '}':
                        depth -= 1
                        if depth == 0:
                            try:
                                parsed = json.loads(content[start:i+1])
                                break
                            except json.JSONDecodeError:
                                pass
            except Exception:
                pass

        if not parsed:
            # 无法解析 JSON，构造一个默认结果（但先尝试从 content 中提取分数）
            # 尝试正则搜索分数
            score_match = re.search(r'(?:overall_score|总分|分数)[:\s]*(\d+)', content, re.IGNORECASE)
            fallback_score = int(score_match.group(1)) if score_match else 0
            parsed = {
                "overall_status": "FAIL" if fallback_score < 70 else "CONDITIONAL_PASS",
                "overall_score": fallback_score,
                "summary": "审核 Agent 返回格式错误，已从文本中提取分数" if fallback_score > 0 else "审核 Agent 返回格式错误，无法解析 JSON",
                "details": {},
                "critical_issues": [{"severity": "CRITICAL" if fallback_score == 0 else "HIGH", "category": "审核流程", "description": "审核 Agent 返回了非标准 JSON 格式", "suggestion": "请优化 prompt 让 LLM 只返回 JSON"}] if fallback_score == 0 else [],
                "verdict": "无法判定，需人工审核" if fallback_score == 0 else f"自动判定：{fallback_score}分"
            }

        # 确保 overall_score 存在
        if "overall_score" not in parsed:
            # 尝试从其他键获取
            for key in ["score", "total_score", "rating"]:
                if key in parsed:
                    parsed["overall_score"] = parsed[key]
                    break
            else:
                parsed["overall_score"] = 0

        # 将解析后的 JSON 作为 content 返回（字符串形式，方便 _extract_score 解析）
        return self.format_result(task, json.dumps(parsed, ensure_ascii=False), parsed)
