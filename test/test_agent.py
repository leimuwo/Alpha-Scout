from core.agent import AlphaScoutAgent
import sys
import os

# Add parent directory to path to allow importing core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_agent():
    """
    测试Alpha Scout Agent功能的入口函数
    """
    print("测试Alpha Scout功能 (非 LangGraph 版本)...")
    
    # 1. 创建初始状态
    user_input = input("请输入您的金融问题（例如：分析苹果公司的股票情况）：")
    
    messages = [
        {"role": "user", "content": user_input}
    ]
    
    print("\n正在处理您的请求...\n")
    
    # 2. 运行 Agent
    try:
        agent = AlphaScoutAgent()
        result = agent.invoke(messages)
        
        # 3. 打印最终响应
        final_response = result["messages"][-1]
        print(f"\n💬 AI 响应:\n{final_response['content']}")
                    
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent()
