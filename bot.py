import discord, asyncio, os, re
from selenium import webdriver
from selenium.webdriver.opera.options import Options
from selenium.webdriver.opera.service import Service
from pymongo import MongoClient

# --- Variables d'environnement ---
TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
LOG_CHANNEL_ID = 141500000000000000  # Remplace par ton salon de logs

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

async def log_error(message):
    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"⚠️ {message}")
    print(message)

# --- URL Generator ---
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

# --- Selenium headless (OperaDriver) ---
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Remplace le chemin par le chemin vers ton operadriver.exe
    service = Service("C:/chemin/vers/operadriver.exe")
    driver = webdriver.Opera(service=service, options=options)
    return driver

# --- Initialisation des annonces vues ---
async def init_seen_ids(driver):
    for channel_id, criteria in SALON_CRITERIA.items():
        page = 1
        while True:
            url = generate_vinted_url(criteria, page)
            try:
                driver.get(url)
                items = driver.find_elements_by_css_selector("div.feed-grid__item, div.catalog-items__item")
                if not items:
                    break
                for item in items:
                    link_tag = item.find_element_by_tag_name("a")
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
                    items = driver.find_elements_by_css_selector("div.feed-grid__item, div.catalog-items__item")
                    if not items:
                        break
                    new_found = False
                    for item in items:
                        link_tag = item.find_element_by_tag_name("a")
                        link = link_tag.get_attribute("href")
                        match = re.search(r'-(\d+)(?:\?|$)', link)
                        item_id = match.group(1) if match else link
                        if seen_col.find_one({"channel": channel_id, "item_id": item_id}):
                            continue
                        seen_col.insert_one({"channel": channel_id, "item_id": item_id})
                        new_found = True
                        title = item.get_attribute("data-title") or "No title"
                        price = item.get_attribute("data-price") or "N/A"
                        img_tag = item.find_elements_by_tag_name("img")
                        image_url = img_tag[0].get_attribute("src") if img_tag else None
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
    driver = get_driver()
    await init_seen_ids(driver)
    client.loop.create_task(check_vinted(driver))

client.run(TOKEN)
