from langchain_core.tools import tool
from utils.error_handlers import tool_error_handler
import os

proxy = 'http://127.0.0.1:7897' # 代理设置，与其他工具保持一致
os.environ['HTTP_PROXY'] = proxy
os.environ['HTTPS_PROXY'] = proxy

@tool
@tool_error_handler
def analyze_sentiment(ticker: str):
    """
    分析股票的市场情感（通过新闻、社交媒体等）
    返回正面、负面和中性情感的分布情况
    """
    print(f"🔧 Tool: Analyzing sentiment for {ticker}...")
    
    # 由于是示例，这里使用一个模拟的情感分析函数
    # 实际应用中可以使用NewsAPI、Twitter API或其他情感分析服务
    
    # 增强的模拟情感数据，包含详细新闻摘要
    sentiment_data = {
        "ticker": ticker,
        "sentiment_score": 0.75,  # 0-1之间的分数，越高越正面
        "sentiment_distribution": {
            "positive": 0.6,
            "neutral": 0.3,
            "negative": 0.1
        },
        "news_analysis": {
            "total_news_analyzed": 25,
            "time_range": "过去7天",
            "top_news": [
                {
                    "title": f"{ticker}公布了超出预期的季度财报",
                    "summary": f"{ticker}今天公布了2024财年Q2季度财报，营收达到1200亿美元，同比增长8%，超出市场预期的1150亿美元。净利润为320亿美元，同比增长10%。",
                    "source": "财经新闻网",
                    "publish_time": "2024-01-25 08:30:00",
                    "sentiment": "positive",
                    "sentiment_score": 0.9
                },
                {
                    "title": "分析师上调了对苹果的目标价",
                    "summary": "摩根士丹利分析师将苹果目标价从280美元上调至300美元，维持'增持'评级。分析师认为苹果的AI战略将成为未来增长的主要驱动力。",
                    "source": "华尔街日报",
                    "publish_time": "2024-01-24 14:45:00",
                    "sentiment": "positive",
                    "sentiment_score": 0.85
                },
                {
                    "title": f"{ticker}推出了新产品线",
                    "summary": f"在今天的产品发布会上，{ticker}推出了全新的MacBook Pro系列和升级版的iPad Pro，搭载了最新的M3芯片。市场反响热烈，股价上涨2%。",
                    "source": "科技评论",
                    "publish_time": "2024-01-23 10:00:00",
                    "sentiment": "positive",
                    "sentiment_score": 0.8
                },
                {
                    "title": f"{ticker}在中国市场面临竞争压力",
                    "summary": f"最新数据显示，{ticker}在中国智能手机市场的份额从去年的18%下降到15%，面临来自本土品牌的激烈竞争。",
                    "source": "市场研究机构",
                    "publish_time": "2024-01-22 09:15:00",
                    "sentiment": "negative",
                    "sentiment_score": 0.3
                }
            ]
        },
        "key_sentiment_drivers": [
            "强劲的财报表现",
            "积极的分析师评级",
            "新产品发布",
            "国际市场竞争压力"
        ]
    }
    
    return sentiment_data

if __name__ == "__main__":
    # 测试用例
    ticker = "AAPL"
    result = analyze_sentiment(ticker)
    print(result)