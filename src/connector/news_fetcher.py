import yfinance as yf
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NewsFetcher:
    def __init__(self):
        self.fetched_news_about_stock = []
        self.fetched_news_general = []

    def get_article_content(self, url):
        """
        Fetches the content of an article from the given URL using Selenium and updates the list of
        fetched news.

        Args:
            url (str): The URL of the article.

        Returns:
            str: The content of the article.
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        
        try:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text() for p in paragraphs])
        except Exception as e:
            content = f"Failed to retrieve the article content: {e}"
        finally:
            driver.quit()
        
        return content

    def fetch_news_about_stock(self, ticker_symbol, num_articles=5):
        """
        Fetches the latest news articles for the given ticker symbol.

        Args:
            ticker_symbol (str): The stock ticker symbol.
            num_articles (int): The number of articles to fetch. Default is 5.

        Returns:
            list: A list of dictionaries containing the title, link, publisher, published time, and content of each article.
        """
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news[:num_articles]
        
        news_list = []
        for article in news:
            publish_time = datetime.fromtimestamp(article['providerPublishTime']).strftime('%Y-%m-%d %H:%M:%S')
            content = self.get_article_content(article['link'])
            news_item = {
                'title': article['title'],
                'link': article['link'],
                'publisher': article['publisher'],
                'published': publish_time,
                'content': content
            }
            news_list.append(news_item)
        
        self.fetched_news = news_list