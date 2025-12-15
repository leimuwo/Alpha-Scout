# 测试脚本：验证A股数据源自动切换功能
from tools.real_time_tool import get_stock_price

print("=== 测试中国股票自动切换数据源 (000001.SZ) ===")
try:
    hist, fundamentals = get_stock_price('000001.SZ')
    print('基本面:', fundamentals)
    print('历史数据行数:', len(hist))
    print('成功获取中国股票数据！')
except Exception as e:
    print('获取中国股票数据失败:', e)

print("\n=== 测试美国股票 (AAPL) ===")
try:
    hist_us, fundamentals_us = get_stock_price('AAPL')
    print('基本面:', fundamentals_us)
    print('历史数据行数:', len(hist_us))
    print('成功获取美国股票数据！')
except Exception as e:
    print('获取美国股票数据失败:', e)