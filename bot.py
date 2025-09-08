import discord
import os
import asyncio
import requests
from bs4 import BeautifulSoup

# === CONFIG BOT ===
TOKEN = os.getenv("TOKEN")  # Ton token Discord
LOG_CHANNEL_ID = 141500000000000000  # Salon pour les logs

# === CRITÈRES POUR CHAQUE SALON ===
# salon_id: critères (marque, catalog, tailles, prix max)
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

# === Fonction pour générer l'URL Vinted ===
def generate_vinted_url(search_text, catalog_ids=None, size_ids=None, price_to=None, order="newest_first"):
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

    if order:
        params.append(f"order={order}")

    return base_url + "&".join(params)


# === Construction automatique de CHANNELS ===
CHANNELS = {salon_id: generate_vinted_url(**criteria) for salon_id, criteria in SALON_CRITERIA.items()}

seen_ids = {channel_id: set() for channel_id in CHANNELS.keys()}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

intents = discord.Intents.default()
client = discord.Client(intents=intents)


# === Fonction pour log dans le salon dédié ===
async def log_error(message):
    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"⚠️ {message}")
    print(message)


# === Boucle de scraping ===
async def check_vinted():
    await client.wait_until_ready()
    while not client.is_closed():
        for channel_id, url in CHANNELS.items():
            channel = client.get_channel(channel_id)
            if not channel:
                await log_error(f"Salon {channel_id} introuvable")
                continue

            try:
                r = requests.get(url, headers=HEADERS, timeout=10)
                if r.status_code != 200:
                    await log_error(f"Erreur HTTP {r.status_code} pour {url}")
                    continue

                soup = BeautifulSoup(r.text, "html.parser")
                items = soup.find_all("div", class_=["feed-grid__item", "catalog-items__item"])
                if not items:
                    await log_error(f"Aucune annonce trouvée pour {url}")
                    continue

                for item in items:
                    link_tag = item.find("a", href=True)
                    if not link_tag:
                        continue
                    link = "https://www.vinted.fr" + link_tag.get("href")
                    item_id = link.split("-")[-1]

                    if item_id in seen_ids[channel_id]:
                        continue
                    seen_ids[channel_id].add(item_id)

                    title_tag = item.find("div", class_=["feed-grid__item-title", "catalog-items__title"])
                    price_tag = item.find("div", class_=["feed-grid__item-price", "catalog-items__price"])
                    title = title_tag.text.strip() if title_tag else "No title"
                    price = price_tag.text.strip() if price_tag else "N/A"

                    msg = f"🔥 Nouvelle annonce : **{title}** - {price}\n{link}"
                    await channel.send(msg)

            except Exception as e:
                await log_error(f"Exception sur {url}: {e}")

        await asyncio.sleep(2)


@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")
    await log_error(f"Bot connecté en tant que {client.user}")
    client.loop.create_task(check_vinted())


client.run(TOKEN)
