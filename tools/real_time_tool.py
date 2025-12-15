import yfinance as yf
import tushare as ts
import akshare as ak
import pandas as pd
import os
from dotenv import load_dotenv
import datetime
# 加载环境变量
load_dotenv()

# 初始化tushare
# 从环境变量获取tushare token，如果没有则使用默认值
TS_TOKEN = os.getenv("TS_TOKEN", "your_tushare_token_here")
ts.set_token(TS_TOKEN)

proxy = 'http://127.0.0.1:7897' # 代理设置，此处修改
os.environ['HTTP_PROXY'] = proxy
os.environ['HTTPS_PROXY'] = proxy

def get_tushare_stock_data(ticker: str):
    """通过tushare获取国内股票数据"""
    print(f"🔧 Tool: Fetching data from tushare for {ticker}...")
    
    # 创建tushare pro接口
    pro = ts.pro_api()
    
    try:
        # 获取股票基本信息
        stock_basic = pro.stock_basic(ts_code=ticker)
        
        if stock_basic.empty:
            raise ValueError(f"股票代码 {ticker} 不存在")
        
        # 获取历史行情数据（最近一年）
        # 计算一年前的日期
        import datetime
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y%m%d")
        
        hist = pro.daily(ts_code=ticker, start_date=start_date, end_date=end_date)
        
        if hist.empty:
            raise ValueError(f"无法获取股票 {ticker} 的历史数据")
        
        # 转换为与yfinance类似的DataFrame格式
        hist['trade_date'] = pd.to_datetime(hist['trade_date'])
        hist = hist.set_index('trade_date')
        hist = hist.sort_index()
        
        # 重命名列以匹配yfinance的格式
        hist = hist.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'vol': 'Volume'
        })
        
        # 获取基本面数据
        fundamentals = {
            "name": stock_basic['name'].iloc[0],
            "sector": stock_basic['industry'].iloc[0],
            "pe_ratio": None,  # tushare需要单独获取
            "market_cap": None,  # tushare需要单独获取
            "forward_pe": None
        }
        
        # 尝试获取更多基本面数据
        try:
            daily_basic = pro.daily_basic(ts_code=ticker, trade_date=end_date)
            if not daily_basic.empty:
                fundamentals["pe_ratio"] = daily_basic['pe_ttm'].iloc[0]
                fundamentals["market_cap"] = daily_basic['circ_mv'].iloc[0] * 10000  # 转换为元
        except:
            pass
            
        return hist, fundamentals
        
    except Exception as e:
        print(f"❌ Error fetching data from tushare: {e}")
        raise

def get_yfinance_stock_data(ticker: str):
    """通过yfinance获取国外股票数据"""
    print(f"🔧 Tool: Fetching data from yfinance for {ticker}...")
    stock = yf.Ticker(ticker)
    
    # 获取最近1年数据用于画图和分析
    hist = stock.history(period="1y")
    
    if hist.empty:
        raise ValueError(f"无法获取股票 {ticker} 的历史数据")
    
    # 获取基本面
    info = stock.info
    fundamentals = {
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "pe_ratio": info.get("trailingPE"),
        "market_cap": info.get("marketCap"),
        "forward_pe": info.get("forwardPE")
    }
    
    return hist, fundamentals

def get_akshare_stock_data(ticker: str):
    """通过akshare获取国内股票数据，作为tushare的备用"""
    print(f"🔧 Tool: Fetching data from akshare for {ticker}...")
    
    # 转换股票代码格式：000001.SZ -> 000001
    # akshare使用的是纯数字代码
    stock_code = ticker.split('.')[0]
    
    # 初始化基本面数据
    fundamentals = {
        "name": stock_code,
        "sector": "未知",
        "pe_ratio": None,
        "market_cap": None,
        "forward_pe": None
    }
    
    # 获取实时行情数据，包含股票名称、市盈率和市值
    try:
        # 获取所有A股的实时行情
        all_stocks = ak.stock_zh_a_spot_em()
        
        # 根据股票代码筛选
        stock_spot = all_stocks[all_stocks['代码'] == stock_code]
        
        # 从实时行情中获取股票信息
        if not stock_spot.empty:
            # 股票名称
            if '名称' in stock_spot.columns:
                fundamentals["name"] = stock_spot['名称'].iloc[0]
            
            # 市盈率（TTM）
            if '市盈率-动态' in stock_spot.columns:
                pe_value = stock_spot['市盈率-动态'].iloc[0]
                if pe_value != '-':
                    fundamentals["pe_ratio"] = float(pe_value)
            
            # 市值（亿元），转换为元
            if '总市值' in stock_spot.columns:
                market_cap_value = stock_spot['总市值'].iloc[0]
                if market_cap_value != '-':
                    fundamentals["market_cap"] = float(market_cap_value) * 1e8
    except Exception as e:
        print(f"⚠️  无法获取实时行情数据: {e}")
    
    # 使用其他函数获取行业信息
    if fundamentals["sector"] == "未知":
        try:
            # 使用stock_individual_info_em获取股票详细信息，包括行业
            stock_detail = ak.stock_individual_info_em(symbol=stock_code)
            
            # 查找行业相关信息
            for index, row in stock_detail.iterrows():
                item = row['item']
                value = row['value']
                if '行业' in item or '板块' in item:
                    fundamentals["sector"] = value
                    break
            
            # 如果还是没有找到行业信息，尝试使用stock_individual_info_bj_a获取
            if fundamentals["sector"] == "未知":
                try:
                    stock_detail_bj = ak.stock_individual_info_bj_a(symbol=stock_code)
                    for index, row in stock_detail_bj.iterrows():
                        item = row['item']
                        value = row['value']
                        if '行业' in item or '板块' in item:
                            fundamentals["sector"] = value
                            break
                except Exception as e:
                    print(f"⚠️  无法从stock_individual_info_bj_a获取行业信息: {e}")
        except Exception as e:
            print(f"⚠️  无法获取详细行业信息: {e}")
    
    # 获取历史行情数据
    try:
        # 设置日期范围为最近一年
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y%m%d")
        
        # 使用stock_zh_a_hist函数获取历史数据
        hist = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="hfq"  # 使用前复权数据
        )
        
        if not hist.empty:
            # 重命名日期列为Date
            if '日期' in hist.columns:
                hist = hist.rename(columns={'日期': 'Date'})
            
            # 设置Date列为索引
            hist['Date'] = pd.to_datetime(hist['Date'])
            hist = hist.set_index('Date')
            hist = hist.sort_index()
            
            # 重命名其他列
            column_mapping = {
                '开盘': 'Open',
                '最高': 'High',
                '最低': 'Low',
                '收盘': 'Close',
                '成交量': 'Volume'
            }
            
            # 只重命名存在的列
            existing_columns = {k: v for k, v in column_mapping.items() if k in hist.columns}
            hist = hist.rename(columns=existing_columns)
            
            return hist, fundamentals
    except Exception as e:
        print(f"⚠️  无法获取历史数据: {e}")
        import traceback
        traceback.print_exc()
    
    # 创建一个包含最近30天的空DataFrame作为回退
    def create_empty_hist():
        dates = pd.date_range(end=datetime.datetime.now(), periods=30, freq='D')
        hist = pd.DataFrame(index=dates)
        hist['Open'] = 0
        hist['High'] = 0
        hist['Low'] = 0
        hist['Close'] = 0
        hist['Volume'] = 0
        return hist
    
    return create_empty_hist(), fundamentals

def get_stock_price(ticker: str, market: str = None):
    """获取股票实时价格和简要基本面
    
    Args:
        ticker: 股票代码
        market: 市场标识，可选值为 'cn'（中国市场）或 'us'（美国市场）
                如果不指定，将根据股票代码自动判断
    """
    print(f"🔧 Tool: Fetching data for {ticker}...")
    
    # 根据市场参数或股票代码后缀自动选择数据源
    if market == 'cn' or (market is None and any(ticker.endswith(suffix) for suffix in ['SH', 'SZ', 'BJ'])):
        # 中国市场股票，先尝试tushare，如果失败则使用akshare
        try:
            return get_tushare_stock_data(ticker)
        except Exception as e:
            print(f"🔄 Tushare获取失败，尝试使用Akshare: {e}")
            return get_akshare_stock_data(ticker)
    elif market == 'us' or (market is None and not any(ticker.endswith(suffix) for suffix in ['SH', 'SZ', 'BJ'])):
        # 美国市场股票，使用yfinance
        return get_yfinance_stock_data(ticker)
    else:
        # 默认使用yfinance
        return get_yfinance_stock_data(ticker)

if __name__ == "__main__":
    # 测试用例
    ticker = "AAPL"
    hist, fundamentals = get_stock_price(ticker)
    print(hist.head())
    print(fundamentals)