import discord
import asyncio
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient

# --- Variables d'environnement ---
TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
LOG_CHANNEL_ID = 1415243356161703997  # Remplace par ton salon de logs si besoin

# --- Multi-salon / critères ---
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

# --- Discord ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# --- MongoDB ---
mongo = MongoClient(MONGO_URI)
db = mongo["vinted_bot"]
seen_col = db["seen_ids"]

# --- Logging des erreurs ---
async def log_error(message):
    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"⚠️ {message}")
    print(message)

# --- Générateur d'URL Vinted ---
def generate_vinted_url(criteria, page=1):
    base = "https://www.vinted.fr/catalog?"
    params = []
    if criteria.get("search_text"):
        params.append(f"search_text={criteria['search_text'].replace(' ', '+')}")
    for c in criteria.get("catalog_ids", []):
        params.append(f"catalog[]={c}")
    for s in criteria.get("size_ids", []):
        params.append(f"size_ids[]={s}")
    if criteria.get("price_to"):
        params.append(f"price_to={criteria['price_to']}")
    params.append("order=newest_first")
    params.append(f"page={page}")
    return base + "&".join(params)

# --- Selenium headless ---
def get_driver():
    print("🔹 Création des options Chrome...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # CHEMIN du binaire Chromium dans le conteneur Linux
    options.binary_location = "/usr/bin/chromium-browser"  
    print(f"🔹 Vérification du binaire Chromium : {os.path.exists(options.binary_location)}")

    # Installation / récupération du ChromeDriver compatible
    print("🔹 Installation/Utilisation de ChromeDriver via webdriver-manager...")
    driver_path = ChromeDriverManager().install()
    print(f"🔹 ChromeDriver installé ici : {driver_path}")
    service = Service(driver_path)

    print("🔹 Démarrage de ChromeDriver...")
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ ChromeDriver démarré avec succès !")
    return driver

# --- Initialisation des annonces vues ---
async def init_seen_ids(driver):
    for channel_id, criteria in SALON_CRITERIA.items():
        page = 1
        while True:
            url = generate_vinted_url(criteria, page)
            try:
                driver.get(url)
                print(f"🔹 Page chargée pour init : {url}")
                items = driver.find_elements(By.CSS_SELECTOR, "div.feed-grid__item, div.catalog-items__item")
                if not items:
                    break
                for item in items:
                    link_tag = item.find_element(By.TAG_NAME, "a")
                    link = link_tag.get_attribute("href")
                    match = re.search(r'-(\d+)(?:\?|$)', link)
                    item_id = match.group(1) if match else link
                    if not seen_col.find_one({"channel": channel_id, "item_id": item_id}):
                        seen_col.insert_one({"channel": channel_id, "item_id": item_id})
            except Exception as e:
                await log_error(f"Init Exception sur {url}: {e}")
                break
            page += 1
    await log_error("✅ Initialisation terminée : seules les nouvelles annonces seront envoyées.")

# --- Boucle principale pour vérifier les nouvelles annonces ---
async def check_vinted(driver):
    await client.wait_until_ready()
    while not client.is_closed():
        for channel_id, criteria in SALON_CRITERIA.items():
            channel = client.get_channel(channel_id)
            if not channel:
                await log_error(f"Salon {channel_id} introuvable")
                continue
            page = 1
            while True:
                url = generate_vinted_url(criteria, page)
                try:
                    driver.get(url)
                    print(f"🔹 Page chargée : {url}")
                    items = driver.find_elements(By.CSS_SELECTOR, "div.feed-grid__item, div.catalog-items__item")
                    if not items:
                        break
                    new_found = False
                    for item in items:
                        link_tag = item.find_element(By.TAG_NAME, "a")
                        link = link_tag.get_attribute("href")
                        match = re.search(r'-(\d+)(?:\?|$)', link)
                        item_id = match.group(1) if match else link
                        if seen_col.find_one({"channel": channel_id, "item_id": item_id}):
                            continue
                        seen_col.insert_one({"channel": channel_id, "item_id": item_id})
                        new_found = True
                        title = item.get_attribute("data-title") or "No title"
                        price = item.get_attribute("data-price") or "N/A"
                        img_tag = item.find_element(By.TAG_NAME, "img")
                        image_url = img_tag.get_attribute("src") if img_tag else None
                        embed = discord.Embed(title=f"{title} - {price}", url=link, color=0xFF5733)
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
    try:
        driver = get_driver()
    except Exception as e:
        await log_error(f"❌ Impossible de démarrer ChromeDriver : {e}")
        return
    await init_seen_ids(driver)
    client.loop.create_task(check_vinted(driver))

client.run(TOKEN)
