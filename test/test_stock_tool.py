# 测试脚本：验证增强后的实时股票数据工具
from tools.real_time_tool import get_stock_price

print("=== 测试美国股票 (AAPL) ===")
try:
    hist, fundamentals = get_stock_price('AAPL')
    print('基本面:', fundamentals)
    print('历史数据行数:', len(hist))
    print('成功获取美国股票数据！')
except Exception as e:
    print('获取美国股票数据失败:', e)

print("\n=== 测试中国股票 (000001.SZ) ===")
try:
    hist_cn, fundamentals_cn = get_stock_price('000001.SZ')
    print('基本面:', fundamentals_cn)
    print('历史数据行数:', len(hist_cn))
    print('成功获取中国股票数据！')
except Exception as e:
    print('中国股票测试可能失败（需要有效的tushare token）:', e)

print("\n=== 测试强制使用yfinance (市场参数) ===")
try:
    hist_force_us, fundamentals_force_us = get_stock_price('MSFT', market='us')
    print('基本面:', fundamentals_force_us)
    print('历史数据行数:', len(hist_force_us))
    print('成功强制使用yfinance获取数据！')
except Exception as e:
    print('强制使用yfinance获取数据失败:', e)