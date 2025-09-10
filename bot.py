import os
import asyncio
import datetime
import logging
from discord import SyncWebhook
from playwright.async_api import async_playwright

# --- Configuration Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VintedBot")

# --- Variables d'environnement ---
DISCORD_TOKEN = os.environ.get("TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("Le token Discord n'est pas défini !")

# --- Configuration des articles à scraper ---
SCRAP_CONFIG = [
    {
        "name": "Stone Island",
        "url": "https://www.vinted.fr/catalog?search_text=stone%20island&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=207&size_ids[]=208&size_ids[]=209&search_id=26351375935&order=newest_first",
        "webhook_url": os.environ.get("STONE_ISLAND_WEBHOOK")  # mettre le webhook Discord
    },
    {
        "name": "CP Company",
        "url": "https://www.vinted.fr/catalog?search_text=cp%20company&catalog[]=79&price_to=80.0&currency=EUR&size_ids[]=208&size_ids[]=207&size_ids[]=209&search_id=26351428301&order=newest_first",
        "webhook_url": os.environ.get("CP_Company_WEBHOOK")
    }
]

SCRAP_INTERVAL = 2  # secondes

# --- Scraping avec Playwright ---
async def scrape_item(page, item_config):
    await page.goto(item_config["url"])
    # Exemple minimal : récupérer les titres des annonces
    titles = await page.eval_on_selector_all(".CatalogItem__title", "elements => elements.map(e => e.textContent)")
    logger.info(f"[{item_config['name']}] {len(titles)} annonces trouvées")
    return titles

# --- Envoi sur Discord ---
async def send_discord_message(webhook_url, message):
    if not webhook_url:
        logger.warning("Webhook non configuré pour cet article.")
        return
    webhook = SyncWebhook.from_url(webhook_url)
    webhook.send(message)

# --- Boucle principale ---
async def main_loop():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        while True:
            for item_config in SCRAP_CONFIG:
                try:
                    titles = await scrape_item(page, item_config)
                    if titles:
                        message = f"Nouvelles annonces {item_config['name']} :\n" + "\n".join(titles[:5])
                        await send_discord_message(item_config["webhook_url"], message)
                except Exception as e:
                    logger.error(f"Erreur scraping {item_config['name']}: {e}")
            await asyncio.sleep(SCRAP_INTERVAL)

# --- Point d'entrée ---
async def main():
    logger.info("=== Démarrage du bot ===")
    await main_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot arrêté manuellement")
