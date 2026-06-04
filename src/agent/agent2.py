import asyncio
import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent, AgentState
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

# 定义图的状态
# class AgentState(TypedDict):
#     messages: Annotated[Sequence[BaseMessage], "messages"]


# 创建 MCP 客户端
client = MultiServerMCPClient(
    {
        "WebParser": {
            "transport": "sse",
            "url": "https://dashscope.aliyuncs.com/api/v1/mcps/WebParser/sse",
            "headers": {
                "Authorization": os.getenv("DASHSCOPE_API_KEY", "")
            }
        },
    }
)

# 创建模型
model = get_model("qwen-plus")

# 创建代理节点
async def agent_node(state: AgentState):
    tools = await client.get_tools()
    agent = create_agent(model, tools)

    response = await agent.ainvoke({"messages": state["messages"]})
    return {"messages": response["messages"]}


# 创建图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("agent", agent_node)

# 设置入口点
workflow.set_entry_point("agent")

# 添加边
workflow.add_edge("agent", END)

# 编译图
agent = workflow.compile()


# 主函数（用于直接运行测试）
async def main():
    messages = [
        HumanMessage(content="你好，你有什么技能？")
    ]

    response = await agent.ainvoke({"messages": messages})
    print_response_details(response)


if __name__ == "__main__":
    print("Starting...")
    asyncio.run(main())
