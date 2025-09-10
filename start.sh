#!/bin/bash
# --- start.sh pour le bot Discord / Vinted ---

echo "=== Démarrage du bot ==="
date

# Mettre à jour pip et installer les dépendances (au cas où)
pip install --upgrade pip
pip install -r requirements.txt

# Installer les navigateurs Playwright (Chromium)
playwright install chromium

# Lancer le bot
python bot.py
