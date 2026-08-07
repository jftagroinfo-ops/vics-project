import requests
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

# Configuration
NEWS_FILE = 'news.json'
# Google News RSS for Indian Agricultural Exports
RSS_URL = 'https://news.google.com/rss/search?q=Indian+Agriculture+Export+Rice+Spices+Trade&hl=en-IN&gl=IN&ceid=IN:en'

def fetch_agro_news():
    print(f"[{datetime.now()}] Fetching live Agro-Trade news...")
    try:
        response = requests.get(RSS_URL, timeout=15)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        news_items = []
        
        for item in root.findall('.//item')[:15]:
            title = item.find('title').text
            # Remove source name from title (usually ends with " - Source")
            clean_title = title.split(' - ')[0]
            
            # Simple keyword filtering to ensure relevance
            keywords = ['rice', 'grain', 'spice', 'export', 'trade', 'wheat', 'sugar', 'agriculture', 'farming', 'commodity', 'port', 'shipping', 'basmati', 'maize', 'crop', 'market']
            if any(key in clean_title.lower() for key in keywords):
                news_items.append({
                    "title": clean_title,
                    "date": item.find('pubDate').text
                })
        
        if not news_items:
            print("No relevant agro news found today, keeping existing data.")
            return

        with open(NEWS_FILE, 'w', encoding='utf-8') as f:
            json.dump(news_items, f, indent=4)
            
        print(f"Successfully updated {len(news_items)} agro news items.")

    except Exception as e:
        print(f"Error fetching news: {e}")

if __name__ == "__main__":
    fetch_agro_news()
