#!/bin/bash

echo "=== Lancement du bot ==="

# Logs environnement
echo "Date: $(date)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Chromium path: $CHROME_BIN"

# Test rapide de connexion à MongoDB
echo "=== Test de connexion à MongoDB ==="
python - <<END
import os
from pymongo import MongoClient, errors

mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://gaspardrtw_db_user:Gaspsuze82@cluster0.agaqelz.mongodb.net/vinted_bot?retryWrites=true&w=majority&tls=true&appName=Cluster0")
try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ Connexion MongoDB réussie")
except errors.ServerSelectionTimeoutError as err:
    print("❌ Impossible de se connecter à MongoDB :", err)
END

# Lancement réel du bot
echo "=== Lancement réel du bot ==="
python main.py
