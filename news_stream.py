import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from newsapi import NewsApiClient

load_dotenv()

API_KEY = os.getenv('NEWS_API_KEY')
newsapi = NewsApiClient(api_key=API_KEY)


async def fetch_news():
    while True:
        try:
            from_date = (datetime.now() - timedelta(weeks=4)).strftime('%Y-%m-%d')
            all_articles = newsapi.get_everything(
                q='technology OR science OR politics OR economics',
                language='en',
                from_param=from_date,
                sort_by='publishedAt',
                page_size=100
            )
            
            for article in all_articles.get('articles', []):
                if(article['title'] == "[REMOVED]"):
                    continue
                yield {
                    'text': f"{article['title']} {article['description']}",
                    'source': article['source']['name'],
                    'timestamp': datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                }
            
            await asyncio.sleep(30)
        
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            await asyncio.sleep(30)

async def start_stream():
    async for article in fetch_news():
        yield article

# This function is used to create a running event loop
def run_stream():
    return asyncio.get_event_loop().run_until_complete(fetch_news())