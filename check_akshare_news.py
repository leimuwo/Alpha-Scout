# -*- coding: utf-8 -*-
import akshare as ak
import pandas as pd
import json

try:
    news_df = ak.stock_news_em(symbol="601658")
    print(f"Columns: {news_df.columns.tolist()}")
    print("\nFirst row:")
    if not news_df.empty:
        with open("news_output.json", "w", encoding="utf-8") as f:
            json.dump(news_df.iloc[0].to_dict(), f, ensure_ascii=False, indent=2)
        print("Written to news_output.json")
except Exception as e:
    print(f"Error: {e}")
