import requests
import os
import json

from connector.news_fetcher import NewsFetcher
from dotenv import load_dotenv

load_dotenv()
web_connector = NewsFetcher()
subscription_key = os.getenv('AZURE_BING_SUBSCRIPTIONKEY')
endpoint = "https://api.bing.microsoft.com/v7.0/search"
with open('ticker_db.json') as f:
    TICKER_OVERVIEW_DB = json.load(f)

def bing_websearch(query):
    """Websearching with bing. It provides a list of hits in form of strings using Selenium and a webdriver.

    Args:
        query (str): query

    Returns:
        list[str]: list of strings according to one hit of the search engine
    """
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key
    }
    params = {
        "q": query,
        "count": 5,
        "mkt": "en-US"
    }

    response = requests.get(endpoint, headers=headers, params=params)
    web_results = []
    if response.status_code == 200:
        results = response.json()
        for result in results.get("webPages", {}).get("value", []):
            search_hit = web_connector.get_article_content(url=result['url'])
            if search_hit and type(search_hit)==str:
                web_results.append("Websearch Title: "+result['name']+"\n"+search_hit)
        return web_results
    else:
        return False
    
def fetch_web_results_on_stock(ticker="AAPL"):
    """Fetch web results on a given stock.

    Args:
        ticker (str): ticker. Defaults to "AAPL".

    Returns:
        list[str]: list of strings according to one hit of the search engine
    """
    selected_companyname = TICKER_OVERVIEW_DB[ticker]
    query = f"latest stock news, earnings report, analyst ratings, recent price movements, short-term catalysts about '{selected_companyname}'"

    return bing_websearch(query=query)

if __name__ == "__main__":
    print(fetch_web_results_on_stock(ticker="MSFT"))