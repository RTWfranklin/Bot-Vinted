#!/bin/bash

# --- Mettre à jour les paquets ---
apt-get update

# --- Installer Chromium et le driver correspondant ---
apt-get install -y chromium chromium-driver

# --- Installer les dépendances Python ---
pip install --upgrade pip
pip install -r requirements.txt

# --- Lancer le bot Python ---
python3 bot.py
