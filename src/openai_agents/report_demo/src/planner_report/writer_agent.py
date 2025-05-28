from agents import Agent
from .context import UserContext

writer_agent = Agent[UserContext](
    name="Writer",
    instructions="""
你是报告撰写助手。输入是一系列要点 (bullet list)。
生成 ≤150 字的中文 Markdown，格式：
### 摘要
...
### 关键数据
...
禁止凭空捏造信息。
""",
    model="gpt-4o-mini",
)
