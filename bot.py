import asyncio
from discord import Client, Webhook
from playwright.async_api import async_playwright
import os
from datetime import datetime

# --- Configuration des URLs et salons Discord ---
ARTICLES = {
    "stone_island": {
        "url": "https://www.vinted.fr/catalog?search_text=stone%20island&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=207&size_ids[]=208&size_ids[]=209&search_id=26351375935&order=newest_first",
        "webhook_url": os.getenv("STONE_ISLAND_WEBHOOK")
    },
    "cp_company": {
        "url": "https://www.vinted.fr/catalog?search_text=cp+company&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=208&size_ids[]=207&size_ids[]=209&search_id=26351428301&order=newest_first",
        "webhook_url": os.getenv("CP_Company_WEBHOOK")
    },
}

SCRAP_INTERVAL = 2  # secondes

# --- Client Discord ---
client = Client(intents=None)

# --- Mémoriser les annonces déjà envoyées ---
seen_items = {key: set() for key in ARTICLES.keys()}


async def scrape_article(playwright, article_key, article_data):
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(article_data["url"])

    items = await page.query_selector_all("div.feed-grid__item")

    new_posts = []
    for item in items:
        link_elem = await item.query_selector("a.feed-grid__item-link")
        if not link_elem:
            continue
        href = await link_elem.get_attribute("href")
        if not href or href in seen_items[article_key]:
            continue
        seen_items[article_key].add(href)
        new_posts.append("https://www.vinted.fr" + href)

    await browser.close()
    return new_posts


async def send_to_discord(webhook_url, messages):
    if not messages:
        return
    try:
        webhook = Webhook.from_url(webhook_url, client=client)
        for msg in messages:
            await webhook.send(msg)
    except Exception as e:
        print(f"Erreur Discord: {e}")


async def main_loop():
    async with async_playwright() as playwright:
        while True:
            for key, data in ARTICLES.items():
                new_posts = await scrape_article(playwright, key, data)
                if new_posts:
                    print(f"[{datetime.now()}] Nouveaux posts pour {key}: {len(new_posts)}")
                await send_to_discord(data["webhook_url"], new_posts)
            await asyncio.sleep(SCRAP_INTERVAL)


@client.event
async def on_ready():
    print(f"=== Bot Discord prêt : {client.user} ===")
    asyncio.create_task(main_loop())


# --- Lancer le bot ---
DISCORD_TOKEN = os.getenv("TOKEN")
client.run(DISCORD_TOKEN)
