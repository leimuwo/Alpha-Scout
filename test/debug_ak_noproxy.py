import akshare as ak
import sys
import io
import os

# Set encoding to utf-8 for windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Unset proxy to test direct connection
if 'HTTP_PROXY' in os.environ:
    del os.environ['HTTP_PROXY']
if 'HTTPS_PROXY' in os.environ:
    del os.environ['HTTPS_PROXY']

print("Testing AkShare stock_news_em for 600519 WITHOUT PROXY")
try:
    df = ak.stock_news_em(symbol="600519")
    print("Columns:", df.columns)
    print("Head:", df.head())
    print("SUCCESS")
except Exception as e:
    print("Error:", e)
    # import traceback
    # traceback.print_exc()
