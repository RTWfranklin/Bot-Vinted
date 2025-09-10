#!/bin/bash
set -e

echo "Starting Container"
echo "=== Démarrage du bot ==="
date
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Chromium path: $CHROME_BIN"
echo "-------------------------------------"

echo "=== Test OpenSSL vers MongoDB Atlas ==="
openssl s_client -connect cluster0.agaqelz.mongodb.net:27017 -CAfile /etc/ssl/certs/mongodb-ca.pem </dev/null || echo "⚠️ OpenSSL test failed"

echo "-------------------------------------"
echo "=== Test de connexion à MongoDB avec PyMongo ==="

python - << 'EOF'
import os, sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGO_URI = "mongodb+srv://gaspardrtw_db_user:Gaspsuze82@cluster0.agaqelz.mongodb.net/vinted_bot?retryWrites=true&w=majority&tls=true&tlsCAFile=/etc/ssl/certs/mongodb-ca.pem"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    print("✅ Connexion MongoDB réussie :", client.server_info()["version"])
except ConnectionFailure as e:
    print("❌ Impossible de se connecter à MongoDB :", e)
EOF

echo "-------------------------------------"
echo "=== Lancement réel du bot ==="
python /app/bot.py
