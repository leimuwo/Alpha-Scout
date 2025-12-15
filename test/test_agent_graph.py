from core.agent_graph import graph
from core.agent_state import AgentState
from langchain_core.messages import HumanMessage, SystemMessage
from core.prompt_templates import SYSTEM_PROMPT

def test_agent_graph():
    """
    测试agent_graph功能的入口函数
    """
    print("测试Agent Graph功能...")
    
    # 1. 创建初始状态（包含用户消息）
    user_input = input("请输入您的金融问题（例如：分析苹果公司的股票情况）：")
    
    initial_state: AgentState = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_input)
        ]
    }
    
    print("\n正在处理您的请求...\n")
    
    # 2. 运行Agent Graph
    try:
        # 使用stream模式运行，实时获取结果
        for chunk in graph.stream(initial_state):
            # 打印每个节点的输出
            for node, output in chunk.items():
                print(f"\n=== {node.upper()} 节点输出 ===")
                
                # 检查是否有工具调用
                if hasattr(output, 'tool_calls') and output.tool_calls:
                    for tool_call in output.tool_calls:
                        print(f"工具调用: {tool_call.function.name}")
                        print(f"参数: {tool_call.function.arguments}")
                
                # 检查是否有文本响应
                if hasattr(output, 'content') and output.content:
                    print(f"文本响应: {output.content}")
                    
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_graph()