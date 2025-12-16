import akshare as ak
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Testing AkShare stock_info_global_cls")
try:
    # This usually returns global rolling news. We might need to filter.
    df = ak.stock_info_global_cls() 
    print("Columns:", df.columns)
    print("Head:", df.head())
    print("SUCCESS")
except Exception as e:
    print("Error:", e)
