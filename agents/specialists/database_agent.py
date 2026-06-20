"""
数据库工程师 Agent
负责 PostgreSQL设计、索引优化、Elasticsearch、数据迁移
"""

from typing import Any, Dict

from ..base_agent import BaseAgent


class DatabaseAgent(BaseAgent):
    """
    数据库工程师 Agent

    专业领域: PostgreSQL 15+、Elasticsearch 8+、Redis 7+
    核心职责:
      1. 数据库表设计与 DDL
      2. 索引优化策略
      3. Elasticsearch 全文搜索配置
      4. Redis 缓存策略设计
      5. 数据迁移与版本管理
    """

    async def design_schema(self, module_name: str, entities: str) -> Dict[str, Any]:
        """设计数据库 Schema"""
        prompt = f"""
请为模块「{module_name}」设计 PostgreSQL 数据库 Schema:

实体: {entities}

输出:
1. 完整的 DDL 建表语句（含约束/外键/注释）
2. 索引设计（B-Tree/GIN/GiST）
3. 枚举类型定义
4. 触发器（如 updated_at 自动更新）
5. 表关系说明（ER图描述）
6. 分区策略（如需要）
"""
        content = await self.call_llm(prompt)
        return {"schema": content}

    async def optimize_query(self, query_description: str) -> Dict[str, Any]:
        """查询优化建议"""
        prompt = f"""
请针对以下查询场景提供 PostgreSQL 优化方案:

场景: {query_description}

输出:
1. 优化后的 SQL 查询
2. 索引建议（含创建语句）
3. EXPLAIN ANALYZE 分析方法
4. 分页优化方案（cursor-based）
5. 读写分离建议
6. 连接池配置建议
"""
        content = await self.call_llm(prompt)
        return {"optimization": content}

    async def setup_elasticsearch(self, index_name: str, fields: str) -> Dict[str, Any]:
        """配置 Elasticsearch 索引"""
        prompt = f"""
请为「{index_name}」配置 Elasticsearch 索引:

字段: {fields}

输出:
1. Index Mapping 定义 (JSON)
2. 中文分词器配置 (ik_max_word)
3. 同义词配置
4. 搜索 DSL 查询示例
5. Go 客户端代码 (olivere/elastic 或 es官方客户端)
6. 数据同步方案（PostgreSQL → ES）
"""
        content = await self.call_llm(prompt)
        return {"es_config": content}

    async def design_cache_strategy(self, scenario: str) -> Dict[str, Any]:
        """设计 Redis 缓存策略"""
        prompt = f"""
请为「{scenario}」设计 Redis 缓存策略:

输出:
1. 缓存 Key 命名规范
2. 缓存数据结构选择（String/Hash/Set/ZSet）
3. 过期时间策略
4. 缓存穿透/击穿/雪崩防护
5. 读写策略（Cache-Aside/Write-Through）
6. Go 代码示例
"""
        content = await self.call_llm(prompt)
        return {"cache_strategy": content}

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理数据库任务"""
        task_type = task.get("subtype", "schema")
        description = task.get("description", "")

        if task_type == "schema":
            result = await self.design_schema(
                task.get("module_name", ""),
                description
            )
        elif task_type == "optimize":
            result = await self.optimize_query(description)
        elif task_type == "elasticsearch":
            result = await self.setup_elasticsearch(
                task.get("index_name", ""),
                description
            )
        elif task_type == "cache":
            result = await self.design_cache_strategy(description)
        else:
            result = await self.design_schema(description, description)

        return self.format_result(task, str(result), result)
