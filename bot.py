import os
import asyncio
from discord import Client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient

# --- Token Discord depuis variable d'environnement ---
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Connexion MongoDB ---
MONGO_URI = os.getenv("MONGO_URI")  # Exemple : "mongodb+srv://user:pass@cluster.mongodb.net/dbname"
client_mongo = MongoClient(MONGO_URI)
db = client_mongo["vinted_bot"]
seen_col = db["seen_items"]

# --- Initialisation client Discord ---
client = Client()

# --- Fonction pour configurer ChromeDriver ---
def get_driver():
    options = Options()
    options.add_argument("--headless=new")  # mode headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"  # chemin du binaire Chromium dans le container

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# --- Fonction pour initialiser les IDs déjà vus ---
async def init_seen_ids(driver):
    urls_to_check = [
        "https://www.vinted.fr/catalog?search_text=stone+island",
        "https://www.vinted.fr/catalog?search_text=cp+company"
    ]
    for url in urls_to_check:
        driver.get(url)
        # Exemple fictif : parser les items et vérifier dans MongoDB
        item_id = "12345"
        channel_id = "general"
        if not seen_col.find_one({"channel": channel_id, "item_id": item_id}):
            seen_col.insert_one({"channel": channel_id, "item_id": item_id})

# --- Événement Discord on_ready ---
@client.event
async def on_ready():
    print(f"[INFO] Connecté en tant que {client.user}")
    driver = get_driver()
    await init_seen_ids(driver)
    driver.quit()
    print("[INFO] Initialisation terminée")

# --- Lancer le bot Discord ---
if __name__ == "__main__":
    client.run(TOKEN)
