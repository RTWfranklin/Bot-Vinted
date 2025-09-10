#!/bin/bash
# --- Script de lancement du bot Discord ---

echo "🔹 Lancement du bot..."

# Optionnel : définir le chemin de Chromium explicitement
export CHROMIUM_BIN=/usr/bin/chromium

python bot.py
