import feedparser
import json
import asyncio
import aiohttp
from datetime import datetime

# Configure RSS sources (Financial focus)
RSS_FEEDS = {
    "cnbc_finance": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
    "oil_price": "https://oilprice.com/rss/main",
    "investing": "https://www.investing.com/rss/news_25.rss"
}

async def fetch_feed(session, name, url):
    try:
        async with session.get(url) as response:
            text = await response.text()
            feed = feedparser.parse(text)
            print(f"✅ Fetched {len(feed.entries)} entries from {name}")
            return feed.entries
    except Exception as e:
        print(f"❌ Error fetching {name}: {e}")
        return []

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(session, name, url) for name, url in RSS_FEEDS.items()]
        results = await asyncio.gather(*tasks)
        
        # Flatten list and simplify structure
        all_news = []
        for entries in results:
            for entry in entries:
                all_news.append({
                    "title": entry.title,
                    "summary": entry.get('summary', entry.get('description', 'Summary unavailable')),
                    "link": entry.link,
                    "published": entry.published,
                })
        
        # Save raw data
        with open("data/raw_news.json", "w") as f:
            json.dump(all_news, f, indent=4)
        print(f"\n🚀 Total news collected: {len(all_news)}. Saved to data/raw_news.json")

if __name__ == "__main__":
    asyncio.run(main())