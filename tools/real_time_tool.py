import yfinance as yf
import pandas as pd
import os

proxy = 'http://127.0.0.1:7897' # 代理设置，此处修改
os.environ['HTTP_PROXY'] = proxy
os.environ['HTTPS_PROXY'] = proxy

def get_realtime_data(ticker: str):
    """获取股票实时价格和简要基本面"""
    print(f"🔧 Tool: Fetching data for {ticker}...")
    stock = yf.Ticker(ticker)
    
    # 获取最近1年数据用于画图和分析
    hist = stock.history(period="1y")
    
    # 获取基本面
    info = stock.info
    fundamentals = {
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "pe_ratio": info.get("trailingPE"),
        "market_cap": info.get("marketCap"),
        "forward_pe": info.get("forwardPE")
    }
    
    return hist, fundamentals

if __name__ == "__main__":
    # 测试用例
    ticker = "AAPL"
    hist, fundamentals = get_realtime_data(ticker)
    print(hist.head())
    print(fundamentals)