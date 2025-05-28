from agents import function_tool, RunContextWrapper
from .context import UserContext

@function_tool
async def web_search(wrapper: RunContextWrapper[UserContext], query: str) -> str:
    """伪 Web 搜索：真实项目可接互联网 / 内部 API"""
    return f"[搜索结果] 关于『{query}』的最新资讯..."
