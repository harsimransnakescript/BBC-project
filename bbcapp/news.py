from newsapi import NewsApiClient
from dotenv import load_dotenv
import os
load_dotenv()


newsapi = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY'))

# /v2/top-headlines
top_headlines = newsapi.get_top_headlines(q='Premier League', category='business', language='en')

# all_articles = newsapi.get_everything(q='Premier League',sources='bbc-news,the-verge',domains='bbc.co.uk,techcrunch.com',from_param='2023-08-16',to='2023-08-18',language='en',sort_by='relevancy',page=2)

all_articles = newsapi.get_everything(q='ben stokes', language='en', sort_by='relevancy', page=1)

for article in all_articles['articles']:
    title = article['title']
    description = article['description']
    image_url = article['urlToImage'] if 'urlToImage' in article else 'No Image Available'
    
    print("Title:", title)
    print("Description:", description)
    print("Image URL:", image_url)
    print("===")

# /v2/top-headlines/sources
sources = newsapi.get_sources()

