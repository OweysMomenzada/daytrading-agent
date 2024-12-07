import requests
import os

from src.connector.news_fetcher import NewsFetcher
from dotenv import load_dotenv

load_dotenv()
web_connector = NewsFetcher()
subscription_key = os.getenv('AZURE_BING_SUBSCRIPTIONKEY')
endpoint = "https://api.bing.microsoft.com/v7.0/search"

def bing_websearch(query):
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

if __name__ == "__main__":
    print(bing_websearch("Microsoft Stock"))