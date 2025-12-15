from core.agent_graph import graph
from core.agent_state import AgentState
from langchain_core.messages import HumanMessage, SystemMessage
from core.prompt_templates import SYSTEM_PROMPT

def simple_test():
    """
    简单测试Agent Graph功能的脚本
    使用预设的问题，无需用户输入
    """
    print("简单测试Agent Graph功能...")
    
    # 使用预设的用户问题
    user_input = "分析苹果公司(AAPL)的股票情况"
    print(f"\n用户问题: {user_input}")
    
    # 创建初始状态
    initial_state: AgentState = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_input)
        ]
    }
    
    print("\n正在处理您的请求...\n")
    
    try:
        # 运行Agent Graph
        final_state = None
        for chunk in graph.stream(initial_state):
            for node, output in chunk.items():
                print(f"\n{'='*40}")
                print(f"=== {node.upper()} 节点输出 ===")
                print(f"{'='*40}")
                
                if node == "agent":
                    # 处理AGENT节点输出
                    print(f"节点类型: {type(node)}")
                    print(f"输出类型: {type(output)}")
                    
                    if isinstance(output, dict) and "messages" in output:
                        for msg in output["messages"]:
                            if hasattr(msg, 'content') and msg.content:
                                print(f"\n💬 AI 响应: {msg.content}")
                            
                            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                print(f"\n🔧 工具调用计划:")
                                for tool_call in msg.tool_calls:
                                    # 适配不同格式的工具调用
                                    if isinstance(tool_call, dict):
                                        # 直接字典格式
                                        tool_name = tool_call.get('name', tool_call.get('function', {}).get('name', '未知工具'))
                                        tool_args = tool_call.get('args', tool_call.get('function', {}).get('arguments', '{}'))
                                        call_id = tool_call.get('id', '无ID')
                                    elif hasattr(tool_call, 'name'):
                                        # 带name属性的对象
                                        tool_name = tool_call.name
                                        tool_args = tool_call.args if hasattr(tool_call, 'args') else {}
                                        call_id = tool_call.id if hasattr(tool_call, 'id') else '无ID'
                                    elif hasattr(tool_call, 'function'):
                                        # 带function属性的对象
                                        tool_name = tool_call.function.name
                                        tool_args = tool_call.function.arguments
                                        call_id = tool_call.id if hasattr(tool_call, 'id') else '无ID'
                                    else:
                                        tool_name = '未知工具'
                                        tool_args = {}
                                        call_id = '无ID'
                                    print(f"   - 工具名称: {tool_name}")
                                    print(f"   - 参数: {tool_args}")
                                    print(f"   - 调用ID: {call_id}")
                                    
                                    # 打印工具调用提示
                                    print(f"\n🔄 正在执行工具: {tool_name}...")
                
                elif node == "tools":
                    # 处理TOOLS节点输出
                    print(f"节点类型: {type(node)}")
                    print(f"输出类型: {type(output)}")
                    
                    if isinstance(output, dict) and "messages" in output:
                        print(f"\n✅ 工具执行结果:")
                        for msg in output["messages"]:
                            if hasattr(msg, 'name') and hasattr(msg, 'content'):
                                tool_name = msg.name
                                result_str = str(msg.content)
                                call_id = msg.tool_call_id if hasattr(msg, 'tool_call_id') else '无ID'
                                print(f"\n   工具名称: {tool_name}")
                                print(f"   调用ID: {call_id}")
                                
                                # 美化输出结果
                                if len(result_str) > 300:
                                    print(f"   执行结果: {result_str[:300]}...(结果过长，完整结果见上面详细输出)")
                                else:
                                    print(f"   执行结果: {result_str}")
                
                else:
                    # 其他类型的节点输出
                    print(f"节点类型: {type(node)}")
                    print(f"输出类型: {type(output)}")
                    print(f"输出内容: {output}")
                    
                    # 如果是字典，显示所有键
                    if isinstance(output, dict):
                        print(f"输出键: {list(output.keys())}")
                
                # 保存最终状态
                if isinstance(output, dict):
                    final_state = output
        
        print("\n=== 测试完成 ===")
        if final_state and "messages" in final_state:
            print(f"\n最终响应: {final_state['messages'][-1].content}")
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()