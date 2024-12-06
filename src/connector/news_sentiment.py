import os
import requests
from dotenv import load_dotenv

class NewsSentiment:
    """
    A class to fetch news sentiment data using the Alpha Vantage API.
    """
    def __init__(self):
        """
        Initializes the NewsSentiment class by loading environment variables
        and retrieving the API key.
        """
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            raise ValueError("API key not found in environment variables")
        self.url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={self.api_key}'
    
    def _process_sentiment_data(self, data, ticker):
        """
        Processes sentiment data and formats it for display.
        
        Args:
            data (list): List of article data dictionaries
            ticker (str): Target ticker symbol to filter for
        
        Returns:
            str: Formatted string of all articles
        """
        articles = []
        for article in data:
            try:
                formatted_article = (
                    f"\nTitle: {article['title']}\n"
                    f"Time Published: {article['time_published']}\n"
                    f"Author: {', '.join(article['authors'])}\n"
                    f"Summary: {article['summary']}\n"
                )
                
                # Add ticker sentiment information - only for target ticker
                if 'ticker_sentiment' in article:
                    for ticker_data in article['ticker_sentiment']:
                        if ticker_data['ticker'] == ticker:
                            formatted_article += "\nTicker Sentiment:\n"
                            formatted_article += (
                                f"Sentiment Score={float(ticker_data['ticker_sentiment_score']):.3f}, "
                                f"Label={ticker_data['ticker_sentiment_label']}, "
                                f"Relevance={float(ticker_data['relevance_score']):.3f}\n"
                            )
                            break
                
                # Add topic relevance scores
                if 'topics' in article:
                    formatted_article += "\nTopic Relevance Scores:\n"
                    for topic in article['topics']:
                        formatted_article += f"- {topic['topic']}: {float(topic['relevance_score']):.3f}\n"
                
                formatted_article += "-" * 80 + "\n"
                articles.append(formatted_article)
                
            except (KeyError, ValueError) as e:
                print(f"Error processing article: {e}")
                continue
        
        return "".join(articles)

    def get_news_sentiment(self, ticker):
        """
        Fetches news sentiment data for a given ticker symbol.

        Parameters:
        ticker (str): The ticker symbol for which to fetch news sentiment.

        Returns:
        dict: The news sentiment data.

        Raises:
        Exception: If the API request fails.
        """
        
        response = requests.get(self.url)
        
        if response.status_code == 200:
            data = response.json()
            return self._process_sentiment_data(data=data["feed"], 
                                                ticker=ticker)
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

# Usage
if __name__ == "__main__":
    news_sentiment = NewsSentiment()
    data = news_sentiment.get_news_sentiment('AAPL')
    print(data)