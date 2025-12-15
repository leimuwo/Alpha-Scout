from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
import os
from dotenv import load_dotenv
from core.agent_state import AgentState
from core.prompt_templates import SYSTEM_PROMPT
from langchain_openai import ChatOpenAI

# 导入工具
from tools.real_time_tool import get_stock_price
from tools.sentiment_tool import analyze_sentiment
from tools.rag_tool import query_financial_reports
from tools.visualization_tool import plot_stock_history

# 1. 准备工具列表
tools = [get_stock_price, analyze_sentiment, query_financial_reports, plot_stock_history]


# 加载环境变量
load_dotenv()

api_key = os.getenv("api_key")
api_base = os.getenv("api_base")

# 2. 初始化 LLM 并绑定工具
# 使用langchain的ChatOpenAI来处理工具调用
llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0,
    openai_api_key=api_key,
    openai_api_base=api_base
)

# 将工具绑定到LLM
llm_with_tools = llm.bind_tools(tools)

# 3. 定义节点函数
def agent_node(state: AgentState):
    """
    Agent 节点：负责调用 LLM 生成下一步动作（文本回复或工具调用）
    """
    messages = state["messages"]
    # 如果是第一条消息，可以在前面加上 SystemPrompt (可选，或者在 app.py 初始化时加)
    # 这里我们简单直接调用
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 4. 构建 Graph
workflow = StateGraph[AgentState, None, AgentState, AgentState](AgentState)

# 添加节点
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

# 设置入口
workflow.set_entry_point("agent")

# 添加边 (Edge)
# conditional_edges: 检查 agent 的输出。如果有 tool_calls，流向 "tools"，否则结束。
workflow.add_conditional_edges(
    "agent",
    tools_condition,
)

# "tools" 执行完后，必须返回 "agent" 让 LLM 解析工具结果
workflow.add_edge("tools", "agent")

# 5. 编译 Graph
graph = workflow.compile()