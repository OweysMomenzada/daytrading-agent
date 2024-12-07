import os
import json

from openai import OpenAI
from dotenv import load_dotenv

from connector import news_fetcher

load_dotenv()

class FinancialAnalystAgent:
    def __init__(self):
        """Initializing OpenAI Client for the Financia lAnalyst Agent
        """
        api_key = os.getenv('OPENAI_KEY')
        self.client = OpenAI(api_key=api_key)
        with open('ticker_db.json') as f:
            self.TICKER_OVERVIEW_DB = json.load(f)
        self.news_fetcher_obj = news_fetcher.NewsFetcher(num_articles=5)

    def generate_financial_evaluation_on_bing_search_engine(self, ticker):
        company_name = self.TICKER_OVERVIEW_DB[ticker]
        websearch_results = self.news_fetcher_obj.fetch_websearch_results_on_stock(ticker=ticker)
        context = "\n".join(websearch_results)
        instruction = f"""You are a financial analyst evaluating the {company_name} ({ticker}) stock for potential day trading with years of experience. Analyze the provided context, which includes recent news, price movements, analyst ratings, and other financial data as well as potential historical events based on your knowlededge. Identify the most relevant and actionable information while avoiding reliance on outdated or irrelevant details.

Provide:
1. A **summary** of the key information influencing short-term price movements.
2. Your **opinion** on whether to pursue day trading this stock today, with reasoning.
3. Specific **guidance** on how to proceed, including strategies or conditions to watch for.

Be concise and ensure your analysis is focused, actionable, and cautious of risks.
"""

        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": instruction},
                {
                    "role": "user",
                    "content": context
                }
            ]
        )

        return completion.choices[0].message