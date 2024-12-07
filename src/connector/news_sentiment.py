import os
import requests
from dotenv import load_dotenv

load_dotenv()

class NewsSentiment:
    """
    A class to fetch news sentiment data using the Alpha Vantage API.
    """
    def __init__(self, relevance_threshold=0.70):
        """
        Initializes the NewsSentiment class by loading environment variables
        and retrieving the API key.
        """
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            raise ValueError("API key not found in environment variables")
        self.relevance_threshold = relevance_threshold

    def _format_timestamp(self, timestamp):
        """Convert AlphaVantage timestamp to readable format"""
        try:
            # Extract date and time parts
            date = timestamp[:8]  # YYYYMMDD
            time = timestamp[9:]  # HHMMSS
            
            # Format date
            year = date[:4]
            month = date[4:6]
            day = date[6:8]
            
            # Format time
            hour = time[:2]
            minute = time[2:4]
            second = time[4:6]
            
            return f"{year}-{month}-{day} {hour}:{minute}:{second}"
        except:
            return timestamp

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
                # Check relevance score first
                if 'ticker_sentiment' in article:
                    relevant_ticker = None
                    for ticker_data in article['ticker_sentiment']:
                        if ticker_data['ticker'] == ticker:
                            if float(ticker_data['relevance_score']) >= self.relevance_threshold:
                                relevant_ticker = ticker_data
                            break
                    
                    # Skip article if relevance threshold not met
                    if not relevant_ticker:
                        continue
                    
                    # Format article only if relevance threshold met
                    formatted_article = (
                        f"\nTitle: {article['title']}\n"
                        f"Time Published: {self._format_timestamp(article['time_published'])}\n"
                        f"Author: {', '.join(article['authors'])}\n"
                        f"Summary: {article['summary']}\n"
                        f"Sentiment Score & Label: {float(article['overall_sentiment_score']):.3f} "
                        f"({article['overall_sentiment_label']})\n"
                    )

                    # Add ticker sentiment
                    formatted_article += "\nTicker Sentiment:\n"
                    formatted_article += (
                        f"Score={float(relevant_ticker['ticker_sentiment_score']):.3f}, "
                        f"Label={relevant_ticker['ticker_sentiment_label']}, "
                        f"Relevance={float(relevant_ticker['relevance_score']):.3f}\n"
                    )
                    
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
        url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={self.api_key}'
        #response = requests.get(self.url) # TODO this must be uncommented
        
        #if response.status_code == 200: # TODO this must be uncommented
        if url:
            data = {"feed": [{'title': 'Apple Unusual Options Activity For December 06 - Apple ( NASDAQ:AAPL ) ', 'url': 'https://www.benzinga.com/insights/options/24/12/42373003/apple-unusual-options-activity-for-december-06', 'time_published': '20241206T205440', 'authors': ['Benzinga Insights'], 'summary': "Deep-pocketed investors have adopted a bullish approach towards Apple AAPL, and it's something market players shouldn't ignore. Our tracking of public options records at Benzinga unveiled this significant move today.", 'banner_image': 'https://www.benzinga.com/files/images/story/2024/1733518477_0.png', 'source': 'Benzinga', 'category_within_source': 'Markets', 'source_domain': 'www.benzinga.com', 'topics': [{'topic': 'Financial Markets', 'relevance_score': '0.866143'}, {'topic': 'Earnings', 'relevance_score': '0.158519'}, {'topic': 'Technology', 'relevance_score': '0.5'}, {'topic': 'Finance', 'relevance_score': '0.5'}], 'overall_sentiment_score': 0.212181, 'overall_sentiment_label': 'Somewhat-Bullish', 'ticker_sentiment': [{'ticker': 'AAPL', 'relevance_score': '0.993896', 'ticker_sentiment_score': '0.365872', 'ticker_sentiment_label': 'Bullish'}, {'ticker': 'MS', 'relevance_score': '0.073546', 'ticker_sentiment_score': '0.023436', 'ticker_sentiment_label': 'Neutral'}]}]}
            #data = response.json() # TODO this must be uncommented
            return self._process_sentiment_data(data=data["feed"], 
                                                ticker=ticker)
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

# Usage
if __name__ == "__main__":
    news_sentiment = NewsSentiment()
    data = news_sentiment.get_news_sentiment('AAPL')
    print(data)