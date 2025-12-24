import pandas as pd
import numpy as np
import os
from typing import Dict, List, Any
from tools.real_time_tool import get_stock_price
from utils.error_handlers import tool_error_handler

@tool_error_handler
def analyze_portfolio(holdings: Dict[str, float]):
    """
    Analyzes a stock portfolio's performance and risk.
    Input: holdings (Dict) - mapping stock tickers to number of shares.
    Example: {"AAPL": 10, "600519.SH": 100}
    Returns: A summary of current value, historical return, and risk metrics (volatility).
    """
    if not holdings:
        return "Error: Portfolio is empty."

    print(f"🔧 Tool: Analyzing portfolio for {list(holdings.keys())}...")
    
    portfolio_data = []
    total_current_value = 0
    
    # Fetch historical data and current price
    prices_df = pd.DataFrame()
    
    for ticker, shares in holdings.items():
        try:
            hist, fundamentals = get_stock_price(ticker)
            if hist.empty:
                print(f"Warning: No data for {ticker}")
                continue
                
            current_price = hist['Close'].iloc[-1]
            stock_value = current_price * shares
            total_current_value += stock_value
            
            # Align daily returns
            returns = hist['Close'].pct_change().dropna()
            prices_df[ticker] = returns
            
            portfolio_data.append({
                "ticker": ticker,
                "name": fundamentals.get("name", ticker),
                "shares": shares,
                "price": round(float(current_price), 2),
                "value": round(float(stock_value), 2)
            })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            
    if prices_df.empty:
        return "Error: Could not retrieve historical data for portfolio analysis."
        
    # Calculate Portfolio Metrics
    # Weights based on current value
    weights = np.array([item['value'] for item in portfolio_data]) / total_current_value
    
    # Portfolio Return (Historical Daily Average -> Annualized)
    avg_returns = prices_df.mean()
    port_return = np.dot(weights, avg_returns) * 252 # 252 trading days
    
    # Portfolio Risk (Standard Deviation -> Annualized Volatility)
    cov_matrix = prices_df.cov() * 252
    port_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    port_volatility = np.sqrt(port_variance)
    
    # Sharpe Ratio (Assuming 3% Risk Free Rate)
    risk_free_rate = 0.03
    sharpe_ratio = (port_return - risk_free_rate) / port_volatility if port_volatility != 0 else 0
    
    analysis = {
        "holding_details": portfolio_data,
        "total_value": round(float(total_current_value), 2),
        "metrics": {
            "annualized_return": f"{round(port_return * 100, 2)}%",
            "annualized_volatility": f"{round(port_volatility * 100, 2)}%",
            "sharpe_ratio": round(float(sharpe_ratio), 2)
        }
    }
    
    return analysis

if __name__ == "__main__":
    # Test
    test_portfolio = {"AAPL": 10, "TSLA": 5}
    print(analyze_portfolio(test_portfolio))
