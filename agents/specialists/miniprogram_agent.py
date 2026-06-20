"""
小程序前端工程师 Agent
负责微信小程序开发、Three.js适配、VantWeapp组件
"""

import re
import json
import os
from typing import Any, Dict

from ..base_agent import BaseAgent


class MiniProgramAgent(BaseAgent):
    """
    小程序前端工程师 Agent

    专业领域: 微信小程序原生开发、Three.js小程序适配、SMPL-X加载
    核心职责:
      1. 小程序页面开发（WXML/WXSS/JS/JSON）
      2. Three.js + threejs-miniprogram 集成
      3. SMPL-X 模型加载与变形控制
      4. VantWeapp 组件集成
      5. 小程序性能优化
      6. 将生成的代码自动写入 clothDiy_miniprogram 目录
    """

    async def create_page(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建小程序页面，并将代码写入文件系统
        task 中包含: page_name, description, output_path
        """
        page_name = task.get("page_name", "index")
        description = task.get("description", "")
        output_path = task.get("output_path", "")
        ui_spec = task.get("ui_spec", "")
        is_3d = task.get("is_3d_page", False)

        # 构建输出目录
        if not output_path:
            output_path = f"/Users/mac/Desktop/clothDiy/clothDiy_miniprogram/pages/{page_name}"
        os.makedirs(output_path, exist_ok=True)

        prompt = f"""
请创建微信小程序页面「{page_name}」的完整代码。

## 页面需求
{description}

## UI 设计规格
{ui_spec[:2000]}

## 技术要求
- 使用微信小程序原生语法（WXML / WXSS / JS / JSON）
- 集成 VantWeapp 组件（如需要）
- 网络请求通过 lib/api.js 封装
- {"3D相关代码使用 lib/ 下的 three.miniprogram.js 模块" if is_3d else ""}

## 输出格式要求（非常重要！）
请严格按照以下格式输出，每个文件用明确的标记分隔：

FILE: {page_name}.wxml
```wxml
（这里写 WXML 代码）
```

FILE: {page_name}.wxss
```wxss
（这里写 WXSS 代码）
```

FILE: {page_name}.js
```javascript
（这里写 JS 代码，含 Page({{}}) 注册）
```

FILE: {page_name}.json
```json
（这里写页面配置 JSON）
```

只输出上述格式，不要添加额外解释。
"""
        content = await self.call_llm(prompt)

        # 解析 content，提取各个文件
        written_files = {}
        file_pattern = re.compile(r'FILE:\s*(\S+)\n```(?:\w+)?\n([\s\S]*?)```', re.MULTILINE)
        matches = file_pattern.findall(content)

        if not matches:
            # 降级：尝试直接搜索代码块
            code_blocks = re.findall(r'```(?:\w+)?\n([\s\S]*?)```', content)
            file_names = ['wxml', 'wxss', 'js', 'json']
            for i, block in enumerate(code_blocks[:4]):
                ext = file_names[i] if i < len(file_names) else f"txt"
                file_path = os.path.join(output_path, f"{page_name}.{ext}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(block.strip())
                written_files[f"{page_name}.{ext}"] = file_path
        else:
            for filename, file_content in matches:
                file_path = os.path.join(output_path, filename)
                os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) != output_path else output_path, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content.strip())
                written_files[filename] = file_path

        # 如果没有匹配到任何文件，将整个内容写入一个 debug 文件
        if not written_files:
            debug_path = os.path.join(output_path, f"{page_name}_raw.txt")
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(content)
            written_files[f"{page_name}_raw.txt"] = debug_path

        return {
            "page_name": page_name,
            "output_path": output_path,
            "written_files": written_files,
            "file_count": len(written_files),
            "raw_content": content[:500],
        }

    async def implement_3d_feature(self, feature: str, context: str = "", output_path: str = "") -> Dict[str, Any]:
        """实现3D相关功能，并写入文件"""
        if not output_path:
            output_path = "/Users/mac/Desktop/clothDiy/clothDiy_miniprogram/lib"
        os.makedirs(output_path, exist_ok=True)

        prompt = f"""
请实现小程序 3D 功能:

功能: {feature}
项目上下文: {context}

技术栈: Three.js + threejs-miniprogram + SMPL-X

请输出完整的 JS 代码文件，包含：
1. Three.js 场景初始化（renderer/camera/scene）
2. 模型加载（GLTFLoader + Draco）
3. 交互控制（拖拽旋转/缩放/平移/双击重置）
4. 拍照截图功能（canvas.toTempFilePath）
5. 保存到相册（wx.saveImageToPhotosAlbum）

输出格式：
FILE: three_helper.js
```javascript
（完整代码）
```
"""
        content = await self.call_llm(prompt)

        # 解析并写入文件
        written_files = {}
        file_pattern = re.compile(r'FILE:\s*(\S+)\n```(?:\w+)?\n([\s\S]*?)```', re.MULTILINE)
        matches = file_pattern.findall(content)
        for filename, file_content in matches:
            file_path = os.path.join(output_path, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content.strip())
            written_files[filename] = file_path

        if not written_files:
            debug_path = os.path.join(output_path, "3d_feature_raw.txt")
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(content)
            written_files["3d_feature_raw.txt"] = debug_path

        return {"code": content, "written_files": written_files}

    async def optimize_performance(self, area: str) -> Dict[str, Any]:
        """性能优化建议"""
        prompt = f"""
请针对小程序「{area}」区域提供性能优化方案:

1. setData 优化策略
2. 列表渲染优化（长列表/虚拟列表）
3. 3D 模型加载优化（Draco压缩/LOD/预加载）
4. 图片懒加载与压缩
5. 分包加载策略
6. 内存管理建议
"""
        content = await self.call_llm(prompt)
        return {"optimization": content}

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理小程序开发任务"""
        task_type = task.get("subtype", "create_page")
        description = task.get("description", "")

        if task_type == "create_page":
            result = await self.create_page(task)
        elif task_type == "3d_feature":
            output_path = task.get("output_path", "/Users/mac/Desktop/clothDiy/clothDiy_miniprogram/lib")
            result = await self.implement_3d_feature(
                description,
                task.get("context", ""),
                output_path
            )
        elif task_type == "optimize":
            result = await self.optimize_performance(description)
        else:
            result = await self.create_page(task)

        # 将 written_files 信息格式化为可读文本，放入 content
        written_summary = ""
        if "written_files" in result:
            written_summary = "写入的文件:\n" + "\n".join(
                f"  - {k}: {v}" for k, v in result["written_files"].items()
            )

        content_str = json.dumps(result, ensure_ascii=False, indent=2) if not written_summary else written_summary + "\n\n" + json.dumps(result, ensure_ascii=False, indent=2)
        return self.format_result(task, content_str, result)
