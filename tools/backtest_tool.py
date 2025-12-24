import pandas as pd
import numpy as np
from tools.real_time_tool import get_stock_price
from utils.error_handlers import tool_error_handler

@tool_error_handler
def backtest_strategy(ticker: str, initial_capital: float = 100000, strategy: str = "SMA_Crossover"):
    """
    Performs a simple backtest for a given stock and strategy.
    Strategy supported: 'SMA_Crossover' (50-day and 200-day Simple Moving Average).
    """
    print(f"🔧 Tool: Backtesting strategy '{strategy}' for {ticker}...")
    
    hist, fundamentals = get_stock_price(ticker)
    if hist.empty or len(hist) < 200:
        return "Error: Insufficient historical data for backtesting (at least 200 days required)."
        
    df = hist[['Close']].copy()
    
    if strategy == "SMA_Crossover":
        # Calculate Moving Averages
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        
        # Signals
        df['Signal'] = 0.0
        df.iloc[50:, df.columns.get_loc('Signal')] = np.where(df['SMA50'][50:] > df['SMA200'][50:], 1.0, 0.0)
        df['Position'] = df['Signal'].diff()
    else:
        return f"Error: Strategy '{strategy}' not supported."

    # Backtest logic
    capital = initial_capital
    position = 0
    shares = 0
    
    backtest_history = []
    
    for date, row in df.iterrows():
        if row['Position'] == 1: # Buy signal
            shares = capital // row['Close']
            capital -= shares * row['Close']
            position = 1
        elif row['Position'] == -1 and position == 1: # Sell signal
            capital += shares * row['Close']
            shares = 0
            position = 0
            
        current_value = capital + (shares * row['Close'])
        backtest_history.append({"date": date, "total_value": current_value})

    final_value = capital + (shares * df['Close'].iloc[-1])
    total_return = (final_value - initial_capital) / initial_capital
    
    # Benchmarking with Buy and Hold
    buy_and_hold_return = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]
    
    results = {
        "ticker": ticker,
        "name": fundamentals.get("name", ticker),
        "initial_capital": initial_capital,
        "final_value": round(float(final_value), 2),
        "total_return": f"{round(total_return * 100, 2)}%",
        "buy_and_hold_return": f"{round(buy_and_hold_return * 100, 2)}%",
        "summary": f"Strategy {strategy} achieved a {round(total_return * 100, 2)}% return compared to {round(buy_and_hold_return * 100, 2)}% for Buy and Hold."
    }
    
    return results

if __name__ == "__main__":
    # Test
    print(backtest_strategy("AAPL"))
