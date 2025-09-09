#!/bin/bash
# Installer Chromium si pas déjà présent
apt-get update
apt-get install -y chromium chromium-driver

# Lancer le bot
python bot.py
