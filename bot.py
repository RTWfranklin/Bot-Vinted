import asyncio
import random
import requests
from bs4 import BeautifulSoup
import discord

# --- Configuration Discord ---
DISCORD_TOKEN = "TOKEN"
client = discord.Client(intents=discord.Intents.default())

# --- Liste des catégories à scrapper ---
categories = [
    {
        "nom": "Stone island",
        "url": "https://www.vinted.fr/catalog?search_text=stone%20island&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=207&size_ids[]=208&size_ids[]=209&search_id=26351375935&order=newest_first",
        "salon_id": 1414204024282026006
    },
    {
        "nom": "CP company",
        "url": "https://www.vinted.fr/catalog?search_text=cp%20company&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=208&size_ids[]=207&size_ids[]=209&search_id=26351428301&order=newest_first",
        "salon_id": 1414648706271019078
    },
]

# --- Stockage des annonces déjà vues ---
annonces_vues = {cat["nom"]: set() for cat in categories}

# --- Scraper Vinted ---
def scraper_vinted(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        annonces = []
        for item in soup.select("a[class*=feed-grid__item]"):
            annonce_id = item.get("href", "")
            titre = item.get("title", "Sans titre")
            url = "https://www.vinted.fr" + annonce_id
            annonces.append({"id": annonce_id, "titre": titre, "url": url})
        return annonces
    except Exception as e:
        print(f"❌ Erreur scrap : {e}")
        return []

# --- Notifier Discord ---
async def notifier_discord(annonce, salon_id):
    salon = client.get_channel(salon_id)
    if salon:
        await salon.send(f"🆕 {annonce['titre']} -> {annonce['url']}")
    else:
        print(f"⚠️ Salon {salon_id} introuvable")

# --- Boucle scrapping pour une catégorie ---
async def scrapper_categorie(cat):
    while True:
        annonces = scraper_vinted(cat["url"])
        for annonce in annonces:
            if annonce["id"] not in annonces_vues[cat["nom"]]:
                annonces_vues[cat["nom"]].add(annonce["id"])
                await notifier_discord(annonce, cat["salon_id"])
        await asyncio.sleep(2)  # Scrappe toutes les 2 secondes

# --- Boucle principale ---
async def main_loop():
    await client.wait_until_ready()
    tasks = [scrapper_categorie(cat) for cat in categories]
    await asyncio.gather(*tasks)

# --- Lancement du bot Discord ---
if __name__ == "__main__":
    client.loop.create_task(main_loop())
    client.run(DISCORD_TOKEN)
