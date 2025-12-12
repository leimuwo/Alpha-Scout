import yfinance as yf
import matplotlib.pyplot as plt
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
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    
    if hist.empty:
        return "No data found for plotting."
    
    plt.figure(figsize=(10, 5))
    plt.plot(hist.index, hist['Close'], label='Close Price')
    plt.title(f"{ticker} Stock Price - {period}")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    
    output_path = "stock_chart.png"
    plt.savefig(output_path)
    plt.close()
    
    return f"Chart generated and saved at {output_path}"