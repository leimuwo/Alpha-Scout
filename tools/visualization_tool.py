import yfinance as yf
import matplotlib
# 使用非交互式后端，避免Tkinter相关错误
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import pandas as pd
from langchain_core.tools import tool
from utils.error_handlers import tool_error_handler

@tool
@tool_error_handler
def plot_stock_history(ticker: str, period: str = "1mo"):
    """
    Generates a price history chart for a stock ticker.
    Period options: 1mo, 3mo, 6mo, 1y, ytd.
    Saves the chart as 'stock_chart.png' and returns the file path.
    """
    # Try to read from local cache first
    cache_path = os.path.join("data_source/stock_cache", f"{ticker}.csv")
    if os.path.exists(cache_path):
        print(f"Visualization: Reading from local cache {cache_path}")
        hist = pd.read_csv(cache_path, index_col=0, parse_dates=True)
    else:
        try:
            # Try generic fetch first (handles A-share vs US share automatically)
            from tools.real_time_tool import get_stock_price
            hist, _ = get_stock_price(ticker)
        except Exception as e:
            print(f"Error using generic fetch: {e}")
            # Fallback to direct yfinance if generic fails (old behavior)
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
    
    if hist.empty:
        return "No data found for plotting."
        
    # Calculate Technical Indicators
    # 1. MACD
    exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
    exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist['MACD'] = macd
    hist['Signal'] = signal
    
    # 2. RSI
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    hist['RSI'] = 100 - (100 / (1 + rs))
    
    # Plotting
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1, 1]})
    
    # Price and MA
    ax1.plot(hist.index, hist['Close'], label='Close Price')
    ax1.plot(hist.index, hist['Close'].rolling(window=20).mean(), label='MA20', alpha=0.7)
    ax1.plot(hist.index, hist['Close'].rolling(window=60).mean(), label='MA60', alpha=0.7)
    ax1.set_title(f"{ticker} Stock Analysis - {period}")
    ax1.set_ylabel("Price")
    ax1.legend()
    ax1.grid(True)
    
    # MACD
    ax2.plot(hist.index, hist['MACD'], label='MACD', color='blue')
    ax2.plot(hist.index, hist['Signal'], label='Signal', color='red')
    ax2.bar(hist.index, hist['MACD'] - hist['Signal'], label='Hist', color='gray', alpha=0.3)
    ax2.set_ylabel("MACD")
    ax2.legend()
    ax2.grid(True)
    
    # RSI
    ax3.plot(hist.index, hist['RSI'], label='RSI', color='purple')
    ax3.axhline(70, linestyle='--', alpha=0.5, color='red')
    ax3.axhline(30, linestyle='--', alpha=0.5, color='green')
    ax3.set_ylabel("RSI")
    ax3.set_xlabel("Date")
    ax3.legend()
    ax3.grid(True)
    
    plt.tight_layout()
    
    output_path = "stock_chart.png"
    plt.savefig(output_path)
    plt.close()
    
    return f"Chart with technical indicators generated and saved at {output_path}"