import feedparser
import json
import asyncio
import aiohttp
import aiofiles
import os

# Configure RSS sources (Financial focus)
RSS_FEEDS = {
    "cnbc_finance": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
    "oil_price": "https://oilprice.com/rss/main",
    "investing": "https://www.investing.com/rss/news_25.rss"
}

# Tracking file to remember what we've already fetched
FETCH_LOG = "data/fetched_urls.log"

async def load_seen_urls():
    """Load history of fetched URLs into a set for O(1) lookup."""
    if not os.path.exists(FETCH_LOG):
        return set()
    async with aiofiles.open(FETCH_LOG, mode='r') as f:
        content = await f.read()
        return set(content.splitlines())

async def save_new_urls(urls):
    """Append new URLs to the tracking log."""
    if not urls:
        return
    async with aiofiles.open(FETCH_LOG, mode='a') as f:
        await f.write("\n".join(urls) + "\n")

async def fetch_feed(session, name, url, seen_urls):
    try:
        async with session.get(url, timeout=15) as response:
            text = await response.text()
            feed = feedparser.parse(text)
            
            # FILTER HERE: Only keep items we haven't seen in previous runs
            new_entries = [
                e for e in feed.entries 
                if e.link not in seen_urls
            ]
            
            if new_entries:
                print(f"✨ {name}: Found {len(new_entries)} NEW articles.")
            return new_entries
    except Exception as e:
        print(f"❌ Error fetching {name}: {e}")
        return []

async def main():
    # 1. Load history
    seen_urls = await load_seen_urls()
    
    async with aiohttp.ClientSession() as session:
        # 2. Fetch all feeds concurrently
        tasks = [fetch_feed(session, name, url, seen_urls) for name, url in RSS_FEEDS.items()]
        results = await asyncio.gather(*tasks)
        
        # Flatten results
        all_new_news = []
        new_urls_to_log = []
        
        for entries in results:
            for entry in entries:
                all_new_news.append({
                    "title": entry.title,
                    "summary": entry.get('summary', entry.get('description', 'No summary')),
                    "link": entry.link,
                    "published": entry.get('published', 'Unknown Date')
                })
                new_urls_to_log.append(entry.link)

        # 3. Only act if there's actually something new
        if all_new_news:
            # Overwrite raw_news.json with ONLY the new batch
            async with aiofiles.open("data/raw_news.json", mode='w') as f:
                await f.write(json.dumps(all_new_news, indent=4))
            
            # Update the permanent history log
            await save_new_urls(new_urls_to_log)
            print(f"🚀 Batch complete. {len(all_new_news)} items ready for AI analysis.")
        else:
            print("😴 No new news across all sources. AI analysis skipped.")
            # Clear raw_news so the AI script doesn't re-process old data
            if os.path.exists("data/raw_news.json"):
                os.remove("data/raw_news.json")

if __name__ == "__main__":
    asyncio.run(main())