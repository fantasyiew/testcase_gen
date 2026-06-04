import asyncio
import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

checkpointer=InMemorySaver()

client = MultiServerMCPClient(
        {
            "WebParser": {
                "transport": "sse",
                # "name": "阿里云百炼_网页解析",
                "url": "https://dashscope.aliyuncs.com/api/v1/mcps/WebParser/sse",
                "headers": {
                    "Authorization": os.getenv("DASHSCOPE_API_KEY", "")
                }
            },
            "math": {
                "transport": "stdio",  # 本地子进程通信
                "command": "python",
                # 您的 math_server.py 文件的绝对路径
                "args": ["D:\\yrzzz\\Pyprojects\\MCPDemo\\src\\agent\\utils\\math_server.py"],
            },
        }
)

async def create_agent_with_tools():
    tools = await client.get_tools()
    return create_agent(
        model,
        tools,
        checkpointer=checkpointer
    )

model=get_model("qwen-plus")
# tools=client.get_tools()

config={
    "configurable":{
        "thread_id":"1"
    }
}


async def main():
    agent = await create_agent_with_tools()
    print("Starting...")
    response1=await agent.ainvoke({"messages": "计算一下(5+6)×12"},config)
    print_response_details(response1)
    print("----------------------------------")
    response2=await agent.ainvoke({"messages":"把刚刚的结果乘以3是多少？"},config    )
    print_response_details(response2)

if __name__ == "__main__":
    asyncio.run(main())