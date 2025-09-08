#!/bin/bash

# Mettre à jour les paquets
apt-get update

# Installer Chromium et toutes les dépendances nécessaires
apt-get install -y chromium chromium-driver libnss3 libgconf-2-4 fonts-liberation libappindicator3-1 xdg-utils

# Installer les dépendances Python
pip install --upgrade pip
pip install -r requirements.txt

# Lancer le bot
python3 bot.py
