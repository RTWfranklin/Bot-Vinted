import discord
import requests
import asyncio
import os

# === CONFIG BOT ===
TOKEN = os.getenv("TOKEN")  # récupère le token depuis Railway

# Dictionnaire : un salon Discord = une recherche Vinted
CHANNELS = {
    1414204024282026006: "https://www.vinted.fr/catalog?search_text=stone%20island&catalog[]=79&price_to=80&currency=EUR&size_ids[]=207&size_ids[]=208&size_ids[]=209&search_id=26351375935&order=newest_first&page=1&time=1757349003",
    1414648706271019078: "https://www.vinted.fr/catalog?search_text=cp%20company&catalog[]=79&price_to=80&currency=EUR&size_ids[]=208&size_ids[]=207&size_ids[]=209&search_id=26351428301&order=newest_first&page=1&time=1757349111",
}

seen_ids = {channel_id: set() for channel_id in CHANNELS.keys()}

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def check_vinted():
    await client.wait_until_ready()

    while not client.is_closed():
        try:
            for channel_id, url in CHANNELS.items():
                channel = client.get_channel(channel_id)
                if not channel:
                    continue

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

        await asyncio.sleep(5)  # vérifie toutes les 5 secondes

@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")

client.loop.create_task(check_vinted())
client.run(TOKEN)
