import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

from utils.myTools import get_model

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
        }
)


model=get_model("qwen-plus")
tools=client.get_tools()
agent = create_agent(
    model,
    tools
)