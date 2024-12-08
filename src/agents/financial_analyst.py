import os
import json

from openai import OpenAI
from dotenv import load_dotenv

from connector import news_fetcher, news_sentiment, technical_indicators

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
        self.news_sentiment_obj = news_sentiment.NewsSentiment(relevance_threshold=0.55)

    def generate_financial_evaluation_on_bing_search_engine(self, ticker):
        """ Generate a financial evaluation on a stock based on Bing search engine results.

        Args:
            ticker (str): The stock ticker to evaluate.

        Returns:    
            str: The generated financial evaluation.
        """
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
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": instruction},
                {
                    "role": "user",
                    "content": context
                }
            ]
        )
        print("Success: Generated Financial Evaluation on Bing Search Engine")
        return completion.choices[0].message.content
    
    def generate_financial_evaluation_on_general_news(self):
        """ Generate a financial evaluation based on general news.

        Returns:
            str: The generated financial evaluation.
        """
        # update the list first.
        combined_context = self.news_fetcher_obj.fetch_latest_news()
        instruction = f"""You are a financial analyst tasked with evaluating a block of financial news, each item provided with a title, publisher, publishing date, and content. Analyze the news collectively, prioritizing the most recent, significant, and impactful stories. You can consider your own expertise about historical events for your analysis.

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
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": instruction},
                {
                    "role": "user",
                    "content": combined_context
                }
            ]
        )
        print("Success: Generated Financial Evaluation on General News")
        return completion.choices[0].message.content
    
    def generate_financial_evaluation_on_stock_news(self, ticker):
        """ Generate a financial evaluation based on stock news.

        Args:
            ticker (str): The stock ticker to evaluate.

        Returns:
            str: The generated financial evaluation.
        """
        # update the list first.
        company_name = self.TICKER_OVERVIEW_DB[ticker]
        combined_context = self.news_fetcher_obj.fetch_news_about_stock(ticker=ticker)        
        instruction = f"""You are a financial analyst evaluating the {company_name} ({ticker}) stock for potential day trading with years of experience. Analyze the provided context, which includes recent news, price movements, analyst ratings, and other financial data as well as potential historical events based on your knowlededge. Identify the most relevant and actionable information while considering recency and relevancy of the given articles.

Provide:
1. A **summary** of the key information influencing short-term price movements.
2. Your **opinion** on whether to pursue day trading this stock today, with reasoning.
3. Specific **guidance** on how to proceed, including strategies or conditions to watch for.

Be concise and ensure your analysis is focused, actionable, and cautious of risks.
"""
        completion = self.client.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": instruction},
                {
                    "role": "user",
                    "content": combined_context
                }
            ]
        )
        print("Success: Generated Financial Evaluation on Stock News")
        return completion.choices[0].message.content
    
    def generate_sentiment_analysis(self, ticker):
        """ generate a sentiment analysis based on the news sentiment data.

        Args:
            ticker (str): The stock ticker to evaluate.

        Returns:
            str: The generated sentiment analysis.
        """
        # update the list first.
        company_name = self.TICKER_OVERVIEW_DB[ticker]
        news_sentiment_context = self.news_sentiment_obj.get_news_sentiment('AAPL')
        
        instruction = f"""You are an financial analyst with a lot of experience understanding the market behaviour based on sentiments. Your task is to analyze the provided sentiment data to form an opinion on whether to engage in daily trading for the {company_name} ({ticker}) stock. Consider the insights from both the sentiment analysis and the content of the feedback.

# Steps

1. **Parse the Data**: Extract key information such as title, time published, author, summary, sentiment scores, and topic relevance scores from the provided feedback list.
   
2. **Analyze Sentiments**:
   - Evaluate the sentiment scores and labels for both the general and ticker-specific sentiments.
   - Consider the sentiment trends, whether they suggest bullish, bearish, or neutral attitudes.
   
3. **Content Analysis**:
   - Assess the summary for any additional context or insights that could influence the decision.
   - Consider the author's background or reliability if possible.
   - Note the publication time for any relevance in temporal trends or recent events.

4. **Evaluate Topic Relevance**:
   - Analyze the topic relevance scores to understand which areas are most impacted (e.g., Financial Markets, Earnings, Technology, Finance).
   - Determine the relevance of these topics to the decision-making process regarding the stock.

5. **Formulate an Opinion**:
   - Integrate the sentiment and content insights to form a holistic view.
   - Decide on a trading strategy (e.g., buy, hold, sell, or no action) based on the combined analysis.

# Output Format

Present your analysis in a detailed written report, structured in paragraphs with comprehensive insights and a clear conclusion on the trading strategy. Begin with a summary of key insights, followed by detailed analysis, and end with a final trading recommendation. 
"""
        completion = self.client.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": instruction},
                {
                    "role": "user",
                    "content": news_sentiment_context
                }
            ]
        )
        print("Success: Generated Sentiment Analysis")
        return completion.choices[0].message.content
    
    def generate_technical_indicator_analysis(self, ticker):
        """ Generate a technical indicator analysis based on the stock ticker.

        Args:
            ticker (str): The stock ticker to evaluate.

        Returns:
            str: The generated technical indicator analysis.
        """
        company_name = self.TICKER_OVERVIEW_DB[ticker]
        technical_indicators_context = technical_indicators.fetch_technical_indicators_of_ticker(ticker=ticker)
        
        instruction = f"""Analyze the technical indicators of a stock from the past 30 days at one-day intervals to generate an opinion about day trading prospects for {company_name} ({ticker}) stock. The data for each day includes:

- RSI: Relative Strength Index
- SMA_20: 20-period Simple Moving Average
- EMA_20: 20-period Exponential Moving Average
- Bollinger Bands: Lower (BBL_20_2.0), Middle (BBM_20_2.0), and Upper (BBU_20_2.0)
- VWAP: Volume-Weighted Average Price
- ATR: Average True Range

Use this data to provide a day trading evaluation for the stock.

# Steps

1. **Data Analysis for Each Technical Indicator:**
   - Evaluate trends and fluctuations in RSI for overbought or oversold conditions.
   - Analyze SMA_20 and EMA_20 to identify momentum and trend direction.
   - Assess the convergence/divergence of Bollinger Bands to detect volatility expansions or contractions.
   - Examine VWAP for price movement relative to average trading volume.
   - Calculate the average ATR for assessing potential price volatility.

2. **Cross-Indicator Analysis:**
   - Combine indicator signals (e.g., RSI with Bollinger Bands) for a more comprehensive analysis.
   - Look for confirmation of trends or reversals by cross-referencing indicators.

3. **Conclusion Formulation:**
   - Synthesize the analysis into a coherent opinion about the stock's suitability for day trading.
   - Consider if the indicators suggest favorable entry and exit points, or potential market risks.

# Output Format

- Provide a detailed paragraph summarizing the assessment.
- State a clear opinion on the day trading prospects of the stock.
- Especially focus on the last three days of the data to ensure the analysis is up-to-date.
"""
        completion = self.client.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": instruction},
                {
                    "role": "user",
                    "content": technical_indicators_context
                }
            ]
        )
        print("Success: Generated Technical Indicator Analysis")
        return completion.choices[0].message.content