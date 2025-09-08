import discord
import requests
import os
from discord.ext import tasks

# === CONFIG BOT ===
TOKEN = os.getenv("TOKEN")  # Récupère le token depuis Railway

# Dictionnaire : un salon Discord = une recherche Vinted
CHANNELS = {
    1414204024282026006: "https://www.vinted.fr/catalog?search_text=stone%20island&catalog[]=79&price_to=80&currency=EUR&size_ids[]=207&size_ids[]=208&size_ids[]=209&search_id=26351375935&order=newest_first&page=1&time=1757349003",
    1414648706271019078: "https://www.vinted.fr/catalog?search_text=cp%20company&catalog[]=79&price_to=80&currency=EUR&size_ids[]=208&size_ids[]=207&size_ids[]=209&search_id=26351428301&order=newest_first&page=1&time=1757349111",
}


# Chaque salon garde une mémoire des IDs déjà vus
seen_ids = {channel_id: set() for channel_id in CHANNELS.keys()}

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@tasks.loop(seconds=5)  # Vérifie toutes les 5 secondes
async def check_vinted():
    """Vérifie les nouvelles annonces Vinted pour chaque recherche."""
    for channel_id, url in CHANNELS.items():
        channel = client.get_channel(channel_id)
        if not channel:
            continue

        try:
            r = requests.get(url).json()
            for item in r.get("items", []):
                if item["id"] not in seen_ids[channel_id]:
                    seen_ids[channel_id].add(item["id"])
                    title = item["title"]
                    price = item["price"]["amount"]
                    link = f"https://www.vinted.fr{item['path']}"

                    msg = f"🔥 Nouvelle annonce : **{title}** - {price}€\n{link}"
                    await channel.send(msg)

        except Exception as e:
            print("Erreur :", e)


@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")
    check_vinted.start()  # Démarre la boucle automatiquement quand le bot est prêt


# Lancement du bot
client.run(TOKEN)
