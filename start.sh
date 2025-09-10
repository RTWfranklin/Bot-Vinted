#!/bin/bash

echo "=== Démarrage du bot ==="
echo "Date: $(date)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Chromium path: $CHROME_BIN"

echo "=== Test de connexion à MongoDB ==="
python - <<END
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

uri = os.environ.get("MONGO_URI")
try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("✅ Connexion à MongoDB réussie !")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"❌ Impossible de se connecter à MongoDB : {e}")
END

echo "=== Lancement réel du bot ==="
python bot.py
