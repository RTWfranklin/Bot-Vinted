import asyncio
import discord
from discord import Webhook, RequestsWebhookAdapter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime

# --- CONFIGURATION ---
DISCORD_TOKEN = "TOKEN"

# Mapping type d'article → ID salon Discord
ARTICLE_CHANNELS = {
    "stone_island": 1414204024282026006,
    "CP company": 1414648706271019078,
    # ajoute autant de types que nécessaire
}

# URLs de scraping par type d'article
ARTICLE_URLS = {
    "stone_island": "https://www.vinted.fr/catalog?search_text=stone%20island&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=207&size_ids[]=208&size_ids[]=209&search_id=26351375935&order=newest_first",
    "CP company": "https://www.vinted.fr/catalog?search_text=cp%20company&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=208&size_ids[]=207&size_ids[]=209&search_id=26351428301&order=newest_first",
}

# --- INITIALISATION CLIENT DISCORD ---
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

# --- Fonction utilitaire pour lancer Chrome headless ---
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# --- Fonction de scrap simple ---
async def scrap_articles(article_type):
    url = ARTICLE_URLS[article_type]
    driver = get_driver()
    try:
        driver.get(url)
        # TODO : Adapter le scraping selon le HTML de Vinted
        items = driver.find_elements("css selector", ".feed-grid__item")
        results = []
        for item in items[:5]:  # On prend uniquement les 5 derniers pour éviter spam
            title = item.text.split("\n")[0]
            link = item.find_element("tag name", "a").get_attribute("href")
            results.append((title, link))
        return results
    finally:
        driver.quit()

# --- Fonction pour envoyer les annonces sur Discord ---
async def send_to_discord(article_type, articles):
    channel_id = ARTICLE_CHANNELS.get(article_type)
    if not channel_id:
        return
    channel = client.get_channel(channel_id)
    if not channel:
        print(f"⚠️ Salon Discord introuvable pour {article_type}")
        return
    for title, link in articles:
        await channel.send(f"**{title}**\n{link}")

# --- Boucle principale ---
async def main_loop():
    while True:
        print(f"[{datetime.utcnow()}] Lancement du scrap...")
        tasks = [scrap_articles(article_type) for article_type in ARTICLE_URLS]
        results = await asyncio.gather(*tasks)
        for article_type, articles in zip(ARTICLE_URLS, results):
            await send_to_discord(article_type, articles)
        await asyncio.sleep(2)  # scrap toutes les 2 secondes

# --- Event on_ready ---
@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")
    client.loop.create_task(main_loop())

# --- Lancement du bot ---
async def main():
    async with client:
        await client.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
