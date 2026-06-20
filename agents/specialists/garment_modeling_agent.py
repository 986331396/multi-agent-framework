"""
服装3D建模师 Agent
负责 Blender建模、MarvelousDesigner、glTF导出、蒙皮绑定
"""

from typing import Any, Dict

from ..base_agent import BaseAgent


class GarmentModelingAgent(BaseAgent):
    """
    服装3D建模师 Agent

    专业领域: Blender 3.6+、Marvelous Designer、glTF/GLB、SMPL骨架蒙皮
    核心职责:
      1. 服装模板建模（Blender）
      2. SMPL骨架蒙皮绑定
      3. BlendShapes/MorphTargets 制作
      4. glTF/GLB 导出与 Draco 压缩
      5. Blender Python 自动化脚本
      6. 质量控制与穿透检测
    """

    async def create_blender_workflow(self, garment_type: str) -> Dict[str, Any]:
        """创建 Blender 建模工作流"""
        prompt = f"""
请为「{garment_type}」创建完整的 Blender 建模标准化流程:

输出:
1. 导入 SMPL-X 参考模型的步骤
2. 服装 Mesh 建模步骤（前后片/袖子/领子等）
3. 面片厚度与细分设置
4. UV 展开与纹理映射
5. 质量控制清单
6. 常见问题与解决方案

参考标准体型: 身高175cm/胸围96cm/腰围80cm/臀围92cm
"""
        content = await self.call_llm(prompt)
        return {"workflow": content}

    async def create_blender_script(self, task_description: str) -> Dict[str, Any]:
        """生成 Blender Python 自动化脚本"""
        prompt = f"""
请生成 Blender Python API 自动化脚本:

任务: {task_description}

输出完整的 Python 脚本，可直接在 Blender 中运行:
1. 完整的 bpy 代码
2. 注释说明每个步骤
3. 错误处理
4. 参数化配置（可通过命令行传参）
"""
        content = await self.call_llm(prompt)
        return {"script": content}

    async def create_skinning_guide(self, garment_type: str) -> Dict[str, Any]:
        """创建蒙皮绑定指南"""
        prompt = f"""
请为「{garment_type}」创建 SMPL 骨架蒙皮绑定指南:

输出:
1. Data Transfer / Copy Weight 操作步骤
2. 关节处权重调整方法（肩部/肘部/腰部）
3. BlendShapes 制作方案:
   - 方式A（完整版）: 10个 BlendShapes
   - 方式B（快速版）: 3个 BlendShapes + 程序化缩放
4. 穿透检测方法
5. 验证流程（旋转手臂测试）
6. 常见穿透问题修复
"""
        content = await self.call_llm(prompt)
        return {"skinning_guide": content}

    async def create_gltf_export_script(self) -> Dict[str, Any]:
        """生成 glTF 导出脚本"""
        prompt = f"""
请生成 Blender glTF/GLB 导出 Python 脚本:

要求:
- 启用 Draco 压缩（级别6）
- 包含 BlendShapes (shapekeys) 数据
- 包含蒙皮 (skins) 信息
- 包含变形目标 (morph targets)
- 纹理使用 JPEG 格式

输出:
1. 完整的 bpy 导出脚本
2. 命令行批量导出版本
3. 导出后验证脚本（检查文件完整性）
4. 体积优化建议
"""
        content = await self.call_llm(prompt)
        return {"export_script": content}

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理3D建模任务"""
        task_type = task.get("subtype", "workflow")
        description = task.get("description", "")

        if task_type == "workflow":
            result = await self.create_blender_workflow(description)
        elif task_type == "script":
            result = await self.create_blender_script(description)
        elif task_type == "skinning":
            result = await self.create_skinning_guide(description)
        elif task_type == "export":
            result = await self.create_gltf_export_script()
        else:
            result = await self.create_blender_workflow(description)

        return self.format_result(task, str(result), result)
