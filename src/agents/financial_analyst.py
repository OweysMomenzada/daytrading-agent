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
    
    def generate_financial_evaluation_on_general_news(self, ticker):
        # update the list first.
        self.news_fetcher_obj.fetch_latest_news(ticker=ticker)
        self.news_fetcher_obj.fetched_news_general
        contexts = "\n".join(self.news_fetcher_obj.fetched_news_general)

        combined_context = ""
        for item in contexts:
            combined_context += f"Newstitle: {item['title']}\n"
            combined_context += f"Publisher: {item['publisher']}\n"
            combined_context += f"Published: {item['published']}\n"
            combined_context += f"Content: {item['content']}\n\n"

        
        instruction = f"""You are a financial analyst tasked with evaluating a block of financial news, each item provided with a title, publisher, publishing date, and content. Analyze the news collectively, prioritizing the most recent, significant, and impactful stories.

For the news block as a whole:
1. **Recency Filter**: Assess the collective recency of the news and identify the most relevant time-sensitive items.
2. **Key Themes and Significance**: Summarize the major themes or topics emerging from the news, highlighting stories with the greatest potential market impact (e.g., major economic indicators, policy changes, sector disruptions, or corporate announcements).
3. **Market Implications**: Evaluate how the combined information might influence the financial market or specific sectors.
4. **Actionable Insights**: Provide overall recommendations for investors or traders based on the summarized analysis.

Your response should include:
- A concise **summary** of the most important and relevant news.
- An **analysis** of the broader implications for the financial market or key sectors.
- Recommendations on how to navigate the market based on this news block.

Focus on clarity, brevity, and actionable insights while filtering out irrelevant or outdated information."
"""

        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": instruction},
                {
                    "role": "user",
                    "content": combined_context
                }
            ]
        )

        return completion.choices[0].message