import asyncio
import os
from datetime import datetime
from discord import Client, Intents
from playwright.async_api import async_playwright

# --- Configuration des URLs Vinted et des salons Discord ---
ARTICLES = {
    "stone_island": {
        "url": "https://www.vinted.fr/catalog?search_text=stone%20island&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=207&size_ids[]=208&size_ids[]=209&order=newest_first",
        "channel_id": int(os.getenv("STONE_ISLAND_CHANNEL"))
    },
    "CP Company": {
        "url": "https://www.vinted.fr/catalog?search_text=cp+company&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=207&size_ids[]=208&size_ids[]=209&order=newest_first",
        "channel_id": int(os.getenv("CP_COMPANY_CHANNEL"))
    }
}

SCRAP_INTERVAL = 10  # secondes
client = Client(intents=Intents.default())

# --- Mémoriser les annonces déjà envoyées ---
seen_items = {key: set() for key in ARTICLES.keys()}

async def scrape_article(playwright, article_key, article_data):
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(article_data["url"])

    items = await page.query_selector_all("div.feed-grid__item")
    new_posts = []
    all_posts = []

    for item in items:
        link_elem = await item.query_selector("a.feed-grid__item-link")
        if not link_elem:
            continue
        href = await link_elem.get_attribute("href")
        url = "https://www.vinted.fr" + href
        all_posts.append(url)

        if href not in seen_items[article_key]:
            seen_items[article_key].add(href)
            new_posts.append(url)

    await browser.close()

    # Logs
    print(f"[{datetime.now()}] {article_key} - annonces scrapées ({len(all_posts)}):")
    for post in all_posts:
        print(f"   - {post}")

    return new_posts

async def send_to_discord(channel_id, messages):
    if not messages:
        return
    channel = client.get_channel(channel_id)
    if not channel:
        print(f"Erreur: salon Discord {channel_id} introuvable")
        return
    for msg in messages:
        try:
            await channel.send(msg)
        except Exception as e:
            print(f"Erreur envoi Discord: {e}")

async def main_loop():
    async with async_playwright() as playwright:
        while True:
            for key, data in ARTICLES.items():
                try:
                    new_posts = await scrape_article(playwright, key, data)
                    if new_posts:
                        print(f"[{datetime.now()}] Nouveaux posts pour {key}: {len(new_posts)}")
                        await send_to_discord(data["channel_id"], new_posts)
                except Exception as e:
                    print(f"[{datetime.now()}] Erreur récupération {key}: {e}")
            await asyncio.sleep(SCRAP_INTERVAL)

@client.event
async def on_ready():
    print(f"=== Bot Discord prêt : {client.user} ===")
    asyncio.create_task(main_loop())

# --- Lancer le bot ---
DISCORD_TOKEN = os.getenv("TOKEN")
client.run(DISCORD_TOKEN)
