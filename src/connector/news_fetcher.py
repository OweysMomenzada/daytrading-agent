import requests
import os
import json

import yfinance as yf
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

class NewsFetcher:
    def __init__(self, num_articles=5):
        """Initializes the NewsFetcher with an empty list of fetched news.

        Args:
            num_articles (int): The number of articles to fetch. Default is 5.
        """
        self.fetched_news_about_stock = []
        self.fetched_news_general = []
        self.fetched_websearch_about_stock = []
        self.num_articles = num_articles
        self.subscription_key = os.getenv('AZURE_BING_SUBSCRIPTIONKEY')
        self.endpoint = "https://api.bing.microsoft.com/v7.0/search"
        with open('ticker_db.json') as f:
            self.TICKER_OVERVIEW_DB = json.load(f)

    def get_article_content(self, url):
        """
        Fetches the content of an article from the given URL using Selenium and updates the list of
        fetched news.

        Args:
            url (str): The URL of the article.

        Returns:
            str: The content of the article.
        """
        print(f"Fetching article content from {url}")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        
        try:
            WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text() for p in paragraphs])
        except Exception as e:
            content = f"Failed to retrieve the article content: {e}"
        finally:
            driver.quit()
        
        return content
    
    def bing_websearch(self, query):
        """Websearching with bing. It provides a list of hits in form of strings using Selenium and a webdriver.

        Args:
            query (str): query

        Returns:
            list[str]: list of strings according to one hit of the search engine
        """
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }
        params = {
            "q": query,
            "count": 7,
            "mkt": "en-US"
        }

        response = requests.get(self.endpoint, headers=headers, params=params)
        web_results = []
        if response.status_code == 200:
            results = response.json()
            for result in results.get("webPages", {}).get("value", []):
                search_hit = self.get_article_content(url=result['url'])
                if search_hit and type(search_hit)==str:
                    web_results.append("Websearch Title: "+result['name']+"\n"+search_hit)
            return web_results
        else:
            print(response.json())
            return False
        
    def fetch_news_and_update(self, ticker_symbol, list_of_news_to_update):
        """
        Fetches the latest news articles for the given ticker symbol.
        If the article content is not available, it will be set to "Failed to retrieve the article content".
        Otherwise, the content will be fetched using the get_article_content method.

        Args:
            ticker_symbol (str): The stock ticker symbol.
            list_of_news_to_update (list): The list of news to update.

        Returns:
            list: A list of dictionaries containing the title, link, publisher, published time, and content of each article.
        """
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news[:self.num_articles]
        
        existing_links = {item['link'] for item in list_of_news_to_update}
        updated = False
        
        for article in news:
            if article['link'] not in existing_links:
                publish_time = datetime.fromtimestamp(article['providerPublishTime']).strftime('%Y-%m-%d %H:%M:%S')
                content = self.get_article_content(article['link'])
                news_item = {
                    'title': article['title'],
                    'link': article['link'],
                    'publisher': article['publisher'],
                    'published': publish_time,
                    'content': content
                }
                list_of_news_to_update.insert(0, news_item)
                updated = True
        
        list_of_news_to_update = list_of_news_to_update[:self.num_articles]
        
        return list_of_news_to_update if updated else False

    def fetch_latest_news(self):
        """
        Fetches the latest news for the given ticker symbol from Yahoo Finance for S&P 500.

        Returns:
            list: A list of dictionaries containing the title, link, publisher, published time, and content of each news article.
        """
        result = self.fetch_news_and_update(ticker_symbol="^GSPC", 
                                            list_of_news_to_update=self.fetched_news_general)
        if not result:
            return False
        else:
            self.fetched_news_general = result
            output_text = []
            for news_item in self.fetched_news_general:
                title = f"Title: {news_item['title']}"
                publisher = f"Publisher: {news_item['publisher']}"
                published = f"Published at: {news_item['published']}"
                content = f"Content: {news_item['content']}"

                output_text.append(f"\n{title}\n{publisher}\n{published}\n{content}\n")
            return "\n".join(output_text)

    def fetch_news_about_stock(self, ticker):
        """
        Fetches the latest news for the given ticker symbol from Yahoo Finance.

        Args:
            ticker_symbol (str): The stock ticker symbol.

        Returns:
            list: A list of dictionaries containing the title, link, publisher, published time, and content of each news article.
        """
        result = self.fetch_news_and_update(ticker_symbol=ticker, 
                                            list_of_news_to_update=self.fetched_news_about_stock)
        if not result:
            return False
        else:
            self.fetched_news_about_stock = result
            output_text = []
            for news_item in self.fetched_news_about_stock:
                title = f"Title: {news_item['title']}"
                publisher = f"Publisher: {news_item['publisher']}"
                published = f"Published at: {news_item['published']}"
                content = f"Content: {news_item['content']}"

                output_text.append(f"\n{title}\n{publisher}\n{published}\n{content}\n")
            return "\n".join(output_text)
        
    def fetch_websearch_results_on_stock(self, ticker="AAPL"):
        """Fetch web results on a given stock.

        Args:
            ticker (str): ticker. Defaults to "AAPL".

        Returns:
            list[str]: list of strings according to one hit of the search engine
        """
        selected_companyname = self.TICKER_OVERVIEW_DB[ticker]
        query = f"latest stock news, earnings report, analyst ratings, recent price movements, short-term catalysts about '{selected_companyname}'"

        return self.bing_websearch(query=query)
    
if __name__ == "__main__":
    news_fetcher = NewsFetcher(num_articles=2)
    ticker_symbol = "MSFT"
    news_stock = news_fetcher.fetch_news_about_stock(ticker_symbol)
    news_general = news_fetcher.fetch_latest_news()

    print("News about the stock:")
    for news_item in news_fetcher.fetched_news_about_stock:
        print(news_item)
    
    print("\nLatest news:")
    for news_item in news_fetcher.fetched_news_general:
        print(news_item)

    print("Trying to immediately fetch the news again:")
    news_stock = news_fetcher.fetch_news_about_stock(ticker_symbol)
    news_general = news_fetcher.fetch_latest_news()

    if not news_stock:
        print("No new stock news available.")

    print("Trying to fetch the websearch:")
    websearch_results = news_fetcher.fetch_websearch_results_on_stock(ticker=ticker_symbol)
    print(websearch_results)