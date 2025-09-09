#!/bin/sh
# Installation de Chromium + chromedriver
apt-get update
apt-get install -y chromium chromium-driver

# Lancer ton bot
python3 bot.py
