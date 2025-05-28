import asyncio
from dotenv import load_dotenv
from agents import Runner
from .planner_agent import planner_agent
from .context import UserContext

# Load environment variables from .env file
load_dotenv()

async def main():
    ctx = UserContext()
    res = await Runner.run( starting_agent= planner_agent,
                          input= "请写一份 AI 投资基金市场调研报告，150 字以内",
                          context= ctx
                          )
    print(res.final_output)

if __name__ == "__main__":
    asyncio.run(main())
