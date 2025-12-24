from core.agent import AlphaScoutAgent
from core.agent_state import AgentState

def simple_test():
    """
    简单测试Alpha Scout Agent功能的脚本
    使用预设的问题，无需用户输入
    """
    print("简单测试Alpha Scout功能 (非 LangGraph 版本)...")
    
    # 使用预设的用户问题
    user_input = "帮我分析一下A股里邮储银行的股票情况"
    print(f"\n用户问题: {user_input}")
    
    # 创建初始状态
    messages = [
        {"role": "user", "content": user_input}
    ]
    
    print("\n正在处理您的请求...\n")
    
    try:
        # 初始化 Agent
        agent = AlphaScoutAgent()
        
        # 运行 Agent
        result = agent.invoke(messages)
        
        final_messages = result["messages"]
        
        print("\n" + "="*40)
        print("=== 最终对话历史 ===")
        print("="*40)
        
        for msg in final_messages:
            role = msg["role"].upper()
            content = msg.get("content", "")
            if role == "SYSTEM":
                continue
            
            print(f"\n[{role}]")
            if content:
                print(content)
            
            if "tool_calls" in msg:
                for tc in msg["tool_calls"]:
                    print(f"🔧 计划调用工具: {tc['function']['name']}({tc['function']['arguments']})")
            
            if role == "TOOL":
                print(f"✅ 工具 {msg.get('name')} 返回结果 (前200字): {str(content)[:200]}...")

        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()