import discord
import os
import asyncio
import requests
from bs4 import BeautifulSoup
import re
import json

# === CONFIG BOT ===
TOKEN = os.getenv("TOKEN")
LOG_CHANNEL_ID = 141500000000000000  # Salon logs
SEEN_FILE = "seen_ids.json"          # Fichier pour stocker les IDs vus

# === CRITÈRES POUR CHAQUE SALON ===
SALON_CRITERIA = {
    1414204024282026006: {
        "search_text": "stone island",
        "catalog_ids": [79],
        "size_ids": [207,208,209],
        "price_to": 80
    },
    1414648706271019078: {
        "search_text": "cp company",
        "catalog_ids": [79],
        "size_ids": [207,208,209],
        "price_to": 80
    },
}

# === Générateur automatique d'URLs Vinted par page ===
def generate_vinted_url(search_text, catalog_ids=None, size_ids=None, price_to=None, page=1, order="newest_first"):
    base_url = "https://www.vinted.fr/catalog?"
    params = []

    if search_text:
        params.append(f"search_text={search_text.replace(' ', '+')}")
    if catalog_ids:
        for c in catalog_ids:
            params.append(f"catalog[]={c}")
    if size_ids:
        for s in size_ids:
            params.append(f"size_ids[]={s}")
    if price_to:
        params.append(f"price_to={price_to}")
    params.append(f"order={order}")
    params.append(f"page={page}")

    return base_url + "&".join(params)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# === Charger les IDs vus depuis le fichier ===
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_ids = json.load(f)
        seen_ids = {int(k): set(v) for k, v in seen_ids.items()}
else:
    seen_ids = {channel_id: set() for channel_id in SALON_CRITERIA.keys()}

# === Sauvegarde des IDs vus ===
def save_seen_ids():
    with open(SEEN_FILE, "w") as f:
        json.dump({k: list(v) for k, v in seen_ids.items()}, f)

# === Logs dans Discord ===
async def log_error(message):
    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"⚠️ {message}")
    print(message)

# === Initialisation : remplir seen_ids sans envoyer d'annonces ===
async def init_seen_ids():
    await client.wait_until_ready()
    for channel_id, criteria in SALON_CRITERIA.items():
        if channel_id not in seen_ids:
            seen_ids[channel_id] = set()
        page = 1
        while True:
            url = generate_vinted_url(**criteria, page=page)
            try:
                r = requests.get(url, headers=HEADERS, timeout=10)
                if r.status_code != 200:
                    break
                soup = BeautifulSoup(r.text, "html.parser")
                items = soup.find_all("div", class_=["feed-grid__item", "catalog-items__item"])
                if not items:
                    break
                for item in items:
                    link_tag = item.find("a", href=True)
                    if not link_tag:
                        continue
                    link = link_tag.get("href").strip()
                    if not link.startswith("http"):
                        link = "https://www.vinted.fr" + link
                    match = re.search(r'-(\d+)(?:\?|$)', link)
                    item_id = match.group(1) if match else link
                    seen_ids[channel_id].add(item_id)
            except Exception as e:
                await log_error(f"Exception init_seen_ids sur {url}: {e}")
                break
            page += 1
    save_seen_ids()
    await log_error("✅ Initialisation terminée : seules les nouvelles annonces seront envoyées.")

# === Boucle de scraping principale ===
async def check_vinted():
    await client.wait_until_ready()
    while not client.is_closed():
        for channel_id, criteria in SALON_CRITERIA.items():
            channel = client.get_channel(channel_id)
            if not channel:
                await log_error(f"Salon {channel_id} introuvable")
                continue

            page = 1
            while True:
                url = generate_vinted_url(**criteria, page=page)
                try:
                    r = requests.get(url, headers=HEADERS, timeout=10)
                    if r.status_code != 200:
                        await log_error(f"Erreur HTTP {r.status_code} pour {url}")
                        break

                    soup = BeautifulSoup(r.text, "html.parser")
                    items = soup.find_all("div", class_=["feed-grid__item", "catalog-items__item"])
                    if not items:
                        break

                    new_found = False
                    for item in items:
                        link_tag = item.find("a", href=True)
                        if not link_tag:
                            continue

                        link = link_tag.get("href").strip()
                        if not link.startswith("http"):
                            link = "https://www.vinted.fr" + link

                        match = re.search(r'-(\d+)(?:\?|$)', link)
                        item_id = match.group(1) if match else link

                        if item_id in seen_ids.get(channel_id, set()):
                            continue
                        seen_ids[channel_id].add(item_id)
                        save_seen_ids()
                        new_found = True

                        title_tag = item.find("div", class_=["feed-grid__item-title", "catalog-items__title"])
                        price_tag = item.find("div", class_=["feed-grid__item-price", "catalog-items__price"])
                        title = title_tag.text.strip() if title_tag else "No title"
                        price = price_tag.text.strip() if price_tag else "N/A"

                        img_tag = item.find("img")
                        image_url = img_tag.get("src") if img_tag else None

                        embed = discord.Embed(
                            title=f"{title} - {price}",
                            url=link,
                            color=0xFF5733
                        )
                        if image_url:
                            embed.set_image(url=image_url)

                        await channel.send(embed=embed)

                    if not new_found:
                        break
                    page += 1

                except Exception as e:
                    await log_error(f"Exception sur {url}: {e}")
                    break

        await asyncio.sleep(2)

@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")
    await log_error(f"Bot connecté en tant que {client.user}")
    # Initialiser seen_ids sans poster les anciennes annonces
    await init_seen_ids()
    # Lancer la boucle principale
    client.loop.create_task(check_vinted())

client.run(TOKEN)
