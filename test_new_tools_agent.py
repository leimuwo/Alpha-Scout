from core.agent import AlphaScoutAgent
import sys
import os

def test_portfolio_tool():
    print("\n--- Testing Portfolio Tool ---")
    agent = AlphaScoutAgent()
    # Message implying portfolio analysis
    messages = [{
        "role": "user", 
        "content": "我有一个投资组合：100股苹果(AAPL)，500股贵州茅台(600519)。请帮我分析一下这个组合的风险和回报，并计算夏普比率。"
    }]
    
    result = agent.invoke(messages)
    last_msg = result["messages"][-1]
    print(f"Assistant Response:\n{last_msg['content']}")
    
def test_backtest_tool():
    print("\n--- Testing Backtest Tool ---")
    agent = AlphaScoutAgent()
    # Need a stock with enough history. AAPL is good.
    messages = [{
        "role": "user", 
        "content": "我想验证一下在苹果(AAPL)这只股票上使用双均线策略(SMA Crossover)的历史表现如何？初始资金10万美元。"
    }]
    
    result = agent.invoke(messages)
    last_msg = result["messages"][-1]
    print(f"Assistant Response:\n{last_msg['content']}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "backtest":
        test_backtest_tool()
    else:
        test_portfolio_tool()
