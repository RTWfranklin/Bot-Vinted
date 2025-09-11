# --- Étape 1 : image officielle Python ---
FROM python:3.11-slim

# --- Variables d'environnement pour Playwright ---
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# --- Mise à jour et installation des dépendances système pour Chromium/Playwright ---
RUN apt-get update && apt-get install -y \
    wget curl gnupg libnss3 libatk1.0-0 libcups2 libxcomposite1 libxdamage1 \
    libxrandr2 libxfixes3 libxrender1 libx11-xcb1 libxkbcommon0 libpango-1.0-0 \
    libcairo2 libdbus-1-3 libexpat1 libasound2 libdrm2 libgbm1 libatk-bridge2.0-0 \
    libatspi2.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# --- Créer un dossier de travail ---
WORKDIR /app

# --- Copier requirements et installer ---
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# --- Installer Playwright et tous les navigateurs ---
RUN playwright install --with-deps

# --- Copier le code du bot ---
COPY . .

# --- Commande pour lancer le bot ---
CMD ["python", "bot.py"]
