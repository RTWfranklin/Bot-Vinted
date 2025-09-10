import asyncio
import datetime
import logging
from discord import Client, Intents

# --- Configuration logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VintedBot")

# --- Discord bot token ---
DISCORD_TOKEN = "TOKEN"  # Remplace par ton vrai token

# --- Configuration des scrapers : clé = nom du type d'article ---
SCRAPERS = {
    "stone_island": {
        "url": "https://www.vinted.fr/catalog?search_text=stone%20island&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=207&size_ids[]=208&size_ids[]=209&search_id=26351375935&order=newest_first",
        "channel_id": 1414204024282026006,  # Remplace par l'ID du channel Discord
    },
    "CP Company": {
        "url": "https://www.vinted.fr/catalog?search_text=cp%20company&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=208&size_ids[]=207&size_ids[]=209&search_id=26351428301&order=newest_first",
        "channel_id": 1414648706271019078,
    },
    # Ajoute autant de types que tu veux
}

# --- Initialisation du client Discord ---
intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)

# --- Exemple de fonction de scrap (à remplacer par ton vrai scraper) ---
async def scrape_vinted(search_url: str):
    # Simule le scrap
    await asyncio.sleep(0.5)
    return [{"title": "Exemple article", "price": 50, "url": search_url}]

# --- Envoi dans Discord ---
async def send_to_discord(channel_id, items):
    channel = client.get_channel(channel_id)
    if channel is None:
        logger.warning(f"Channel {channel_id} introuvable.")
        return
    for item in items:
        msg = f"Nouvelle annonce : {item['title']} - {item['price']}€\n{item['url']}"
        await channel.send(msg)
        logger.info(f"Annonce envoyée sur le channel {channel_id}: {item['title']}")

# --- Boucle principale ---
async def main_loop():
    while True:
        for key, config in SCRAPERS.items():
            items = await scrape_vinted(config["url"])
            await send_to_discord(config["channel_id"], items)
        await asyncio.sleep(2)  # Scraper toutes les 2 secondes

# --- Hook pour lancer la boucle après connexion ---
@client.event
async def on_ready():
    logger.info(f"{client.user} connecté sur Discord !")
    asyncio.create_task(main_loop())

# --- Lancer le bot ---
client.run(DISCORD_TOKEN)
