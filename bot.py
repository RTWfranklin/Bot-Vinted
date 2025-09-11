import os
import asyncio
import aiohttp
from discord import Client
from datetime import datetime

# --- Configuration des articles et IDs de salons ---
ARTICLES = {
    "stone_island": {
        "search_id": "26351375935",
        "price_to": 80.0,
        "sizes": [207, 208, 209],
        "channel_id": int(os.getenv("STONE_ISLAND_CHANNEL"))
    },
    "CP Company": {
        "search_id": "26351428301",
        "price_to": 80.0,
        "sizes": [207, 208, 209],
        "channel_id": int(os.getenv("CP_COMPANY_CHANNEL"))
    }
}

SCRAP_INTERVAL = 60  # secondes entre chaque vérification
client = Client(intents=None)

# --- Pour mémoriser les annonces déjà envoyées ---
seen_items = {key: set() for key in ARTICLES.keys()}

# --- Fonction async pour récupérer les annonces Vinted ---
async def get_vinted_items(session, article_data):
    url = "https://www.vinted.fr/api/v2/catalog/items"
    params = {
        "search_id": article_data["search_id"],
        "order": "newest_first",
        "price_to": article_data.get("price_to"),
    }
    for size_id in article_data.get("sizes", []):
        params.setdefault("size_ids[]", []).append(size_id)

    try:
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            items = ["https://www.vinted.fr" + item.get("path", "") for item in data.get("items", [])]
            return items
    except Exception as e:
        print(f"[{datetime.now()}] Erreur récupération Vinted ({article_data['search_id']}): {e}")
        return []

# --- Fonction async pour envoyer les messages Discord ---
async def send_to_discord(channel_id, messages):
    if not messages:
        return
    channel = client.get_channel(channel_id)
    if not channel:
        print(f"[{datetime.now()}] Impossible de récupérer le salon {channel_id}")
        return
    for msg in messages:
        try:
            await channel.send(msg)
        except Exception as e:
            print(f"[{datetime.now()}] Erreur envoi message: {e}")

# --- Boucle principale async de scraping ---
async def main_loop():
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = []
            for key, data in ARTICLES.items():
                tasks.append(process_article(session, key, data))
            await asyncio.gather(*tasks)
            await asyncio.sleep(SCRAP_INTERVAL)

# --- Fonction pour traiter un article ---
async def process_article(session, key, data):
    all_items = await get_vinted_items(session, data)
    new_items = [i for i in all_items if i not in seen_items[key]]

    # Mémoriser uniquement les nouvelles annonces
    for i in new_items:
        seen_items[key].add(i)

    # Log complet pour debug
    print(f"[{datetime.now()}] {key} - annonces scrapées ({len(all_items)}), nouvelles: {len(new_items)})")
    for i in all_items:
        print(f"  - {i}")

    # Envoyer uniquement les nouvelles annonces dans Discord
    if new_items:
        await send_to_discord(data["channel_id"], new_items)

# --- Événement Discord on_ready ---
@client.event
async def on_ready():
    print(f"=== Bot Discord prêt : {client.user} ===")
    asyncio.create_task(main_loop())

# --- Lancer le bot ---
DISCORD_TOKEN = os.getenv("TOKEN")
client.run(DISCORD_TOKEN)
