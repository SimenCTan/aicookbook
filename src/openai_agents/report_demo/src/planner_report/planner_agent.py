from agents import Agent
from .context import UserContext
from .writer_agent import writer_agent
from .tools import web_search

def planner_prompt(wrap, _):
    return f"""
# 研究规划智能体 (LLM 自主决策)

目标：为 {wrap.context.user_name} 生成一份 <AI 投资基金市场调研报告>。

可用工具：
- web_search(query)
- writer_agent

工作流程 (自行决定步数)：
1. 思考需要哪些要点：规模、增长率、头部基金…
2. 调用 web_search 收集数据；只调用一次
3. 用 bullet list 汇总要点
4. handoff 给 writer_agent
5. Writer 返回 Markdown 后直接回复用户
禁止泄漏内部思考 / JSON。
"""

planner_agent = Agent[UserContext](
    name="Planner",
    instructions=planner_prompt,
    tools=[web_search],
    handoffs=[writer_agent],
    model="gpt-4o-mini",
)
