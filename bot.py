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
    "CP Company": {
        "url": "https://www.vinted.fr/catalog?search_text=cp+company&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=208&size_ids[]=207&size_ids[]=209&search_id=26351428301&order=newest_first",
        "webhook_url": os.getenv("CP_COMPANY_WEBHOOK")  # ⚠️ corrige la casse ici
    },
    # Ajouter d'autres articles ici
}

SCRAP_INTERVAL = 5  # secondes (j'ai mis 5 pour éviter trop de spam)

client = Client(intents=None)

# --- Mémoriser les annonces déjà envoyées ---
seen_items = {key: set() for key in ARTICLES.keys()}

async def scrape_article(playwright, article_key, article_data):
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(article_data["url"])

    items = await page.query_selector_all("div.feed-grid__item")

    new_posts = []
    all_posts = []  # pour loguer tout ce qu'on scrap

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

    # Log dans la console TOUTES les annonces vues
    print(f"[{datetime.now()}] {article_key} - annonces scrapées ({len(all_posts)}):")
    for post in all_posts:
        print(f"   - {post}")

    return new_posts

async def send_to_discord(webhook_url, messages):
    if not messages or not webhook_url:
        print(f"[{datetime.now()}] ⚠️ Pas de webhook défini, envoi annulé.")
        return
    webhook = Webhook.from_url(webhook_url, client=client)
    for msg in messages:
        try:
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

    # 🔍 Debug : affichage des webhooks
    print("STONE_ISLAND_WEBHOOK =", os.getenv("STONE_ISLAND_WEBHOOK"))
    print("CP_COMPANY_WEBHOOK   =", os.getenv("CP_COMPANY_WEBHOOK"))

    # Envoi d'un message de test dans chaque webhook
    for key, data in ARTICLES.items():
        if not data["webhook_url"]:
            print(f"[{datetime.now()}] ❌ Aucun webhook configuré pour {key}")
            continue
        try:
            webhook = Webhook.from_url(data["webhook_url"], client=client)
            await webhook.send(f"✅ Bot connecté et prêt à surveiller **{key}**")
            print(f"[{datetime.now()}] Message de test envoyé à {key}")
        except Exception as e:
            print(f"Erreur envoi test webhook {key}: {e}")

    asyncio.create_task(main_loop())

# --- Lancer le bot ---
DISCORD_TOKEN = os.getenv("TOKEN")
client.run(DISCORD_TOKEN)
