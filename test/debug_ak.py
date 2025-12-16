import akshare as ak
import sys
import io

# Set encoding to utf-8 for windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Testing AkShare stock_news_em for 600519")
try:
    df = ak.stock_news_em(symbol="600519")
    print("Columns:", df.columns)
    print("Head:", df.head())
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
