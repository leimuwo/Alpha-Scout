
import os
import sys
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.sentiment_tool import analyze_sentiment
from tools.visualization_tool import plot_stock_history
from tools.rag_tool import query_financial_reports

def test_sentiment():
    print("\nXXX Testing Sentiment Analysis (Moutai 600519)...")
    try:
        # Note: akshare might need string code "600519"
        result = analyze_sentiment.invoke("600519")
        print(result)
    except Exception as e:
        print(f"Sentiment Error: {e}")

def test_chart_indicators():
    print("\nXXX Testing Stock Chart (AAPL)...")
    try:
        result = plot_stock_history.invoke({"ticker": "AAPL", "period": "6mo"})
        print(result)
        if os.path.exists("stock_chart.png"):
            print("Chart file created successfully.")
        else:
            print("Chart file MISSING.")
    except Exception as e:
        print(f"Chart Error: {e}")

def test_rag():
    print("\nXXX Testing RAG (Query)...")
    try:
        # Need a dummy PDF in data_source/rag_data for this to really work
        result = query_financial_reports.invoke("What is the revenue growth?")
        print(result)
    except Exception as e:
        print(f"RAG Error: {e}")

if __name__ == "__main__":
    # test_sentiment()
    # test_chart_indicators()
    test_rag()
