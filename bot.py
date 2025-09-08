import discord
import requests
import os
from discord.ext import tasks

# === CONFIG BOT ===
TOKEN = os.getenv("TOKEN")  # récupère ton token depuis Railway

# Associe chaque salon Discord à une recherche Vinted
CHANNELS = {
    1414204024282026006: "https://www.vinted.fr/api/v2/catalog/items?search_text=stone%20island&catalog_ids=79&price_to=80&currency=EUR&size_ids[]=207&size_ids[]=208&size_ids[]=209&order=newest_first",
    1414648706271019078: "https://www.vinted.fr/api/v2/catalog/items?search_text=cp%20company&catalog_ids=79&price_to=80&currency=EUR&size_ids[]=207&size_ids[]=208&size_ids[]=209&order=newest_first",
}


# Mémoire des annonces déjà envoyées
seen_ids = {channel_id: set() for channel_id in CHANNELS.keys()}

# Headers pour ressembler à un vrai navigateur
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36"
}

# Intents Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)


@tasks.loop(seconds=5)  # vérifie toutes les 5 secondes
async def check_vinted():
    """Vérifie les nouvelles annonces Vinted pour chaque recherche."""
    for channel_id, url in CHANNELS.items():
        channel = client.get_channel(channel_id)
        if not channel:
            continue

        try:
            r = requests.get(url, headers=HEADERS)

            if r.status_code != 200:
                print(f"⚠️ Erreur HTTP {r.status_code} pour {url}")
                continue

            data = r.json()  # essaie de convertir en JSON
            for item in data.get("items", []):
                if item["id"] not in seen_ids[channel_id]:
                    seen_ids[channel_id].add(item["id"])
                    title = item["title"]
                    price = item["price"]["amount"]
                    link = f"https://www.vinted.fr{item['path']}"

                    msg = f"🔥 Nouvelle annonce : **{title}** - {price}€\n{link}"
                    await channel.send(msg)

        except Exception as e:
            print("Erreur :", e)
            print("Réponse brute :", r.text[:200])  # debug (200 premiers caractères)


@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")
    check_vinted.start()  # démarre la boucle quand le bot est prêt


# Lancement du bot
client.run(TOKEN)
