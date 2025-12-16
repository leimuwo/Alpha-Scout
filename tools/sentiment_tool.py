from langchain_core.tools import tool
from utils.error_handlers import tool_error_handler
import os
import akshare as ak
import yfinance as yf
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Proxy settings (consistent with other tools)
proxy = 'http://127.0.0.1:7897'
os.environ['HTTP_PROXY'] = proxy
os.environ['HTTPS_PROXY'] = proxy

@tool
@tool_error_handler
def analyze_sentiment(ticker: str):
    """
    Analyzes market sentiment for a given stock ticker by fetching latest news 
    and using an LLM to evaluate sentiment.
    Supports A-shares (via AkShare) and US shares (via yfinance).
    """
    print(f"🔧 Tool: Analyzing sentiment for {ticker}...")
    
    news_items = []
    stock_name = ticker
    
    # 1. Fetch News
    try:
        # Detect market type roughly
        is_a_share = any(ticker.endswith(suffix) for suffix in ['.SH', '.SZ', '.BJ']) or (ticker.isdigit() and len(ticker) == 6)
        
        if is_a_share:
            # A-Share: AkShare
            # Clean ticker for AkShare (e.g. 600519.SH -> 600519)
            code = ticker.split('.')[0]
            print(f"Fetching A-share news for {code}...")
            
            try:
                # Primary source: EastMoney specific stock news
                news_df = ak.stock_news_em(symbol=code)
                # Take top 10 latest news
                if not news_df.empty:
                    recent_news = news_df.head(10)
                    for _, row in recent_news.iterrows():
                        news_items.append({
                            "title": row.get('title', ''),
                            "summary": row.get('content', '')[:200] + "...", # Truncate content
                            "publish_time": row.get('public_time', ''),
                            "source": "EastMoney"
                        })
            except Exception as e:
                print(f"Warning: Primary news source failed ({e}). Trying fallback (Cailianshe)...")
                # Fallback: Cailianshe Global Rolling News filtered by stock code/name
                try:
                    news_df = ak.stock_info_global_cls()
                    # Filter for code or name (if we had name, but code is safer alias)
                    # We don't have name easily here without another call, so just filter by code or simple heuristic
                    mask = news_df['内容'].str.contains(code) | news_df['标题'].str.contains(code)
                    # If we could get stock name that would be better. 
                    # Let's try to search fast.
                    filtered_news = news_df[mask]
                    
                    if not filtered_news.empty:
                        for _, row in filtered_news.head(5).iterrows():
                            news_items.append({
                                "title": row.get('标题', ''),
                                "summary": row.get('内容', '')[:200] + "...",
                                "publish_time": f"{row.get('发布日期', '')} {row.get('发布时间', '')}",
                                "source": "Cailianshe"
                            })
                except Exception as e2:
                    print(f"Fallback source also failed: {e2}")
        else:
            # US Share: yfinance
            print(f"Fetching US share news for {ticker}...")
            stock = yf.Ticker(ticker)
            news = stock.news
            stock_name = ticker
            
            # Take top 10
            for item in news[:10]:
                news_items.append({
                    "title": item.get('title', ''),
                    "summary": item.get('publisher', '') + ": " + item.get('title', ''), # yf news often has no content body in simple call
                    "publish_time": str(datetime.datetime.fromtimestamp(item.get('providerPublishTime', 0))) if item.get('providerPublishTime') else '',
                    "source": item.get('publisher', 'Yahoo Finance')
                })
                
    except Exception as e:
        return f"Error fetching news: {str(e)}"

    if not news_items:
        return {
            "ticker": ticker,
            "sentiment_score": 0.5,
            "sentiment_distribution": {"neutral": 1.0},
            "news_analysis": {"total_news_analyzed": 0, "note": "No recent news found."}
        }

    # 2. Analyze with LLM
    print(f"Analyzing {len(news_items)} news items with LLM...")
    
    # Load env vars
    api_key = os.getenv("api_key")
    api_base = os.getenv("api_base")
    
    if not api_key:
        return "Error: api_key not found in .env"
        
    llm = ChatOpenAI(
        model="deepseek-chat", # DeepSeek model name
        temperature=0,
        api_key=api_key,
        base_url=api_base
    )
    
    news_text = json.dumps(news_items, ensure_ascii=False, indent=2)
    
    system_prompt = """You are a financial sentiment analyst. Analyze the following news items for a specific stock.
    (Note: The user wants to use Chinese for the final report if the input is Chinese, but the component structure should be English keys)
    
    Output a JSON object with:
    - sentiment_score (float -1.0 to 1.0, where >0 is positive, <0 is negative)
    - sentiment_distribution (positive, neutral, negative probabilities summing to 1.0)
    - summary_analysis (brief explanation of the driving factors, in Chinese)
    - key_drivers (list of strings, max 5 items, in Chinese)
    
    Focus on the impact on the stock price in the short to medium term.
    """
    
    user_prompt = f"Stock: {stock_name}\n\nNews Items:\n{news_text}"
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        # Parse output (handling potential code blocks)
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        analysis_result = json.loads(content)
        
        # Combine with metadata
        final_result = {
            "ticker": ticker,
            "sentiment_score": analysis_result.get("sentiment_score", 0),
            "sentiment_distribution": analysis_result.get("sentiment_distribution", {}),
            "key_drivers": analysis_result.get("key_drivers", []),
            "summary_analysis": analysis_result.get("summary_analysis", ""),
            "news_analysis": {
                "total_news_analyzed": len(news_items),
                "top_news": news_items[:3] # Return top 3 for context
            }
        }
        
        return final_result
        
    except Exception as e:
        return f"Error in LLM analysis: {str(e)}"

if __name__ == "__main__":
    # Test
    print(analyze_sentiment("600519"))