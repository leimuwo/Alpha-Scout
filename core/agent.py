# -*- coding: utf-8 -*-
import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

from core.agent_state import AgentState
from core.prompt_templates import SYSTEM_PROMPT

# Import tools
from tools.real_time_tool import get_stock_price
from tools.sentiment_tool import analyze_sentiment
from tools.rag_tool import query_financial_reports
from tools.visualization_tool import plot_stock_history
from tools.portfolio_tool import analyze_portfolio
from tools.backtest_tool import backtest_strategy

load_dotenv()

class AlphaScoutAgent:
    def __init__(self):
        self.api_key = os.getenv("api_key")
        self.api_base = os.getenv("api_base")
        self.model = "deepseek-chat"
        if not self.api_key:
            raise ValueError("api_key not found in environment variables.")
            
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )
        
        self.tools_map = {
            "get_stock_price": self._get_stock_price_wrapper,
            "analyze_sentiment": analyze_sentiment,
            "query_financial_reports": query_financial_reports,
            "plot_stock_history": plot_stock_history,
            "analyze_portfolio": analyze_portfolio,
            "backtest_strategy": backtest_strategy
        }
        
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "get_stock_price",
                    "description": "Fetch real-time stock price and fundamentals. Supports both US and Chinese markets.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticker": {"type": "string", "description": "Stock ticker symbol, e.g., 'AAPL' or '600519.SH'"},
                        },
                        "required": ["ticker"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_sentiment",
                    "description": "Analyzes market sentiment for a given stock ticker by fetching latest news and evaluating it.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        },
                        "required": ["ticker"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "query_financial_reports",
                    "description": "Searches internal financial reports (PDFs) for relevant information about companies.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query about financial details"},
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "plot_stock_history",
                    "description": "Generates a price history chart with technical indicators (MACD, RSI) for a stock ticker.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticker": {"type": "string", "description": "Stock ticker symbol"},
                            "period": {"type": "string", "description": "Period for historical data, e.g. '1mo', '3mo', '1y'", "default": "1mo"},
                        },
                        "required": ["ticker"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_portfolio",
                    "description": "Analyzes the risk, return, and volatility of a user's stock portfolio.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "holdings": {
                                "type": "object", 
                                "description": "A dictionary where keys are tickers and values are number of shares. Example: {'AAPL': 10, '000001.SZ': 100}",
                                "additionalProperties": {"type": "number"}
                            },
                        },
                        "required": ["holdings"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "backtest_strategy",
                    "description": "Backtests a trading strategy (currently SMA Crossover) for a specific stock.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticker": {"type": "string", "description": "Stock ticker symbol"},
                            "initial_capital": {"type": "number", "description": "Initial capital for backtesting", "default": 100000},
                            "strategy": {"type": "string", "description": "Strategy name, currently supports 'SMA_Crossover'", "default": "SMA_Crossover"},
                        },
                        "required": ["ticker"],
                    },
                },
            },
        ]

    def _get_stock_price_wrapper(self, ticker: str):
        # The tool returns (hist, fundamentals), but the agent needs a string or JSON-serializable output
        try:
            _, fundamentals = get_stock_price(ticker)
            return json.dumps(fundamentals, ensure_ascii=False)
        except Exception as e:
            return f"Error fetching stock price: {str(e)}"

    def invoke(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processes a conversation and returns the updated messages.
        This implements the tool-calling loop manually.
        """
        # Ensure system prompt is present
        if not any(m["role"] == "system" for m in messages):
            messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
            
        current_messages = list(messages)
        
        # Max iteration to prevent infinite loops
        for _ in range(5):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=current_messages,
                tools=self.tools_schema,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # OpenAI response message needs to be converted back to dict for the next call
            msg_dict = {
                "role": "assistant",
                "content": response_message.content,
            }
            if response_message.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    } for tool_call in response_message.tool_calls
                ]
            
            current_messages.append(msg_dict)
            
            if not response_message.tool_calls:
                # No more tools to call, return the final response
                return {"messages": current_messages}
                
            # Execute tool calls
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"Executing tool: {function_name}({function_args})")
                
                tool_func = self.tools_map.get(function_name)
                if tool_func:
                    try:
                        result = tool_func(**function_args)
                    except Exception as e:
                        result = f"Error executing tool: {str(e)}"
                else:
                    result = f"Error: Tool {function_name} not found."
                    
                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(result)
                })
        
        return {"messages": current_messages}

# For backward compatibility or singleton usage
agent = AlphaScoutAgent()
