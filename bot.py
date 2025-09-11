import asyncio
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from discord import Client, Webhook

# --- Configuration des URLs et webhooks ---
ARTICLES = {
    "stone_island": {
        "url": "https://www.vinted.fr/catalog?search_text=stone%20island&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=207&size_ids[]=208&size_ids[]=209&search_id=26351375935&order=newest_first",
        "webhook_url": os.getenv("STONE_ISLAND_WEBHOOK")
    },
    "CP Company": {
        "url": "https://www.vinted.fr/catalog?search_text=cp+company&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=208&size_ids[]=207&size_ids[]=209&search_id=26351428301&order=newest_first",
        "webhook_url": os.getenv("CP_COMPANY_WEBHOOK")
    },
}

SCRAP_INTERVAL = 5  # secondes
client = Client(intents=None)

# --- Mémoriser les annonces déjà envoyées ---
seen_items = {key: set() for key in ARTICLES.keys()}

async def scrape_article(article_key, article_data):
    try:
        response = requests.get(article_data["url"], headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except Exception as e:
        print(f"[{datetime.now()}] Erreur requête {article_key}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("div.feed-grid__item a.feed-grid__item-link")

    new_posts = []
    all_posts = []

    for link in items:
        href = link.get("href")
        if not href:
            continue
        url = "https://www.vinted.fr" + href
        all_posts.append(url)
        if href not in seen_items[article_key]:
            seen_items[article_key].add(href)
            new_posts.append(url)

    # Log toutes les annonces
    print(f"[{datetime.now()}] {article_key} - annonces scrapées ({len(all_posts)}):")
    for post in all_posts:
        print(f"   - {post}")

    return new_posts

async def send_to_discord(webhook_url, messages):
    if not webhook_url:
        print("Webhook non configuré !")
        return
    if not messages:
        return
    webhook = Webhook.from_url(webhook_url, client=client)
    for msg in messages:
        try:
            await webhook.send(msg)
        except Exception as e:
            print(f"Erreur Discord: {e}")

async def main_loop():
    while True:
        for key, data in ARTICLES.items():
            new_posts = await scrape_article(key, data)
            if new_posts:
                print(f"[{datetime.now()}] Nouveaux posts pour {key}: {len(new_posts)}")
                await send_to_discord(data["webhook_url"], new_posts)
        await asyncio.sleep(SCRAP_INTERVAL)

@client.event
async def on_ready():
    print(f"=== Bot Discord prêt : {client.user} ===")

    # Message test pour chaque webhook
    for key, data in ARTICLES.items():
        if data["webhook_url"]:
            try:
                webhook = Webhook.from_url(data["webhook_url"], client=client)
                await webhook.send(f"✅ Bot connecté et prêt à surveiller **{key}**")
                print(f"[{datetime.now()}] Message de test envoyé à {key}")
            except Exception as e:
                print(f"Erreur envoi test webhook {key}: {e}")
        else:
            print(f"Webhook non configuré pour {key}")

    asyncio.create_task(main_loop())

# --- Lancer le bot ---
DISCORD_TOKEN = os.getenv("TOKEN")
client.run(DISCORD_TOKEN)
