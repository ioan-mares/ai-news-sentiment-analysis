import json
import asyncio
import aiofiles # Asynchronous file I/O
import os
from ollama import AsyncClient
from datetime import datetime

ANALYSIS_PROMPT = """
You are a High-Frequency Macro Analyst. Your goal is to differentiate high-impact market movers from daily noise.

SCORING RULES (BE AGGRESSIVE):
- Impact Score (1-10): 
    * 1-3: Market noise, irrelevant.
    * 4-6: Regional news, standard partnerships.
    * 7-8: Major earnings, acquisitions, geopolitical shifts.
    * 9-10: Black Swan events, FED/Central Bank pivots, global supply chain collapse.
- Confidence (0-100): Reflect how clear the link is between the news and the ticker.

MANDATORY: Do not default to 8/80. Use the full spectrum. If a news is critical, go for 9 or 10. If it's speculative, drop confidence to 40-50.
MANDATORY: The "price_impact" field MUST be exactly one of these three strings: "Bullish", "Bearish", or "Neutral". Do not combine them. If the news is mixed, choose the one with the highest long-term probability.

JSON STRUCTURE:
{
  "ticker": "SYMBOL",
  "sector": "SECTOR",
  "price_impact": "Bullish/Bearish/Neutral",
  "impact_score": 1-10,
  "confidence": 0-100,
  "logic": "Brief aggressive explanation"
}
"""

async def load_processed_data(filepath="data/processed_news.json"):
    """Read existing data without blocking the event loop."""
    if not os.path.exists(filepath):
        return []
    async with aiofiles.open(filepath, mode='r') as f:
        content = await f.read()
        return json.loads(content) if content else []

async def save_processed_data(data, filepath="data/processed_news.json"):
    """Write results back to disk asynchronously."""
    async with aiofiles.open(filepath, mode='w') as f:
        # We use a thread-safe way to dump JSON to string, then write it
        content = json.dumps(data, indent=4)
        await f.write(content)

async def analyze_item(client, news_item):
    """Async AI inference using Llama 3.1."""
    try:
        response = await client.chat(
            model='llama3.1:latest',
            messages=[
                {'role': 'system', 'content': ANALYSIS_PROMPT},
                {'role': 'user', 'content': f"Title: {news_item['title']}\nSummary: {news_item['summary']}"}
            ],
            format='json'
        )
        analysis = json.loads(response['message']['content'])
        news_item.update(analysis)
        news_item['analyzed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return news_item
    except Exception as e:
        print(f"⚠️ AI Error: {e}")
        return None

async def main():
    # 1. Load data asynchronously
    raw_news = await load_processed_data("data/raw_news.json")
    existing_data = await load_processed_data("data/processed_news.json")
    
    existing_links = {item['link'] for item in existing_data}
    new_items = [item for item in raw_news if item['link'] not in existing_links]

    if not new_items:
        print("☕ No new news to process.")
        return

    print(f"🚀 AI Engine: Analyzing {len(new_items)} new items...")
    
    client = AsyncClient()
    tasks = [analyze_item(client, item) for item in new_items]
    
    # Run all AI inferences concurrently
    results = await asyncio.gather(*tasks)
    
    # 2. Update and save asynchronously
    valid_results = [r for r in results if r is not None]
    updated_final_data = existing_data + valid_results
    
    await save_processed_data(updated_final_data)
    print(f"✅ Success! Database updated with {len(valid_results)} new analyzed items.")

if __name__ == "__main__":
    asyncio.run(main())