import asyncio
import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

from utils.myTools import get_model


async def main():
    client = MultiServerMCPClient(
        {
            # "math": {
            #     "transport": "stdio",  # 本地子进程通信
            #     "command": "python",
            #     # 您的 math_server.py 文件的绝对路径
            #     "args": ["D:\\yrzzz\\Pyprojects\\MCPDemo\\math_server.py"],
            # },
            # "weather": {
            #     "transport": "streamable_http",  # 基于 HTTP 的远程服务器
            #     # 确保您在 8000 端口启动了您的天气服务器
            #     "url": "http://localhost:8000/mcp",
            # },
            # "fetch": {
            #     "transport": "streamable_http",
            #     "url": "https://mcp.api-inference.modelscope.net/ec85a43b7c884f/mcp"
            # },

            "WebParser": {
                "transport": "sse",
                # "name": "阿里云百炼_网页解析",
                "url": "https://dashscope.aliyuncs.com/api/v1/mcps/WebParser/sse",
                "headers": {
                    "Authorization": os.getenv("DASHSCOPE_API_KEY", "")
                }
            },
            # "playwright": {
            #     "transport":"stdio",
            #     "args": [
            #         "-y",
            #         "@automatalabs/mcp-server-playwright"
            #     ],
            #     "command": "npx"
            # }
            # "chrome-devtools": {
            #     "transport":"stdio",
            #     "args": [
            #         "chrome-devtools-mcp@latest"
            #     ],
            #     "command": "npx"
            # }

        }
    )

    # "qwen-plus"
    # "deepseek-chat" X
    model=get_model("qwen-plus")
    tools = await client.get_tools()
    agent = create_agent(
        model,
        tools
    )
    messages= [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there! How can I help you today?"}
    ]

    response = await agent.ainvoke(
        # {"messages":"请描述一下该网页https://www.ctrip.com/中，预定酒店搜索框内有哪些元素内容？"}
        {"messages": "你好，你有什么技能？"}
        # {"messages": "请你描述一下网页https://www.12306.cn/index/中，车票查询框内有哪些元素内容？"}
    )

    print_response_details(response)

if __name__ == "__main__":
    print("Starting...")
    asyncio.run(main())
