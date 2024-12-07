import os

from openai import OpenAI
from dotenv import load_dotenv

from connector import websearcher

load_dotenv()

class FinancialAnalystAgent:
    def __init__(self):
        """Initializing OpenAI Client for the Financia lAnalyst Agent
        """
        api_key = os.getenv('OPENAI_KEY')
        self.client = OpenAI(api_key=api_key)

    def generate_financial_evaluation_on_bing_search_engine(self, ticker):
        company_name = websearcher.TICKER_OVERVIEW_DB[ticker]
        bing_results = websearcher.fetch_web_results_on_stock(ticker=ticker)
        bing_results = "\n".join(bing_results)
        instruction = f"""You are a financial analyst evaluating the {company_name} ({ticker}) stock for potential day trading with years of experience. Analyze the provided context, which includes recent news, price movements, analyst ratings, and other financial data as well as potential historical events based on your knowlededge. Identify the most relevant and actionable information while avoiding reliance on outdated or irrelevant details.

Provide:
1. A **summary** of the key information influencing short-term price movements.
2. Your **opinion** on whether to pursue day trading this stock today, with reasoning.
3. Specific **guidance** on how to proceed, including strategies or conditions to watch for.

Be concise and ensure your analysis is focused, actionable, and cautious of risks.
"""

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": instruction},
                {
                    "role": "user",
                    "content": bing_results
                }
            ]
        )

        return completion.choices[0].message