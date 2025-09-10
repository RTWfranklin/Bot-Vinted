# --- Image de base Python slim ---
FROM python:3.11-slim

# --- Répertoire de travail ---
WORKDIR /app

# --- Copier les fichiers du projet ---
COPY . .

# --- Installer certificats SSL (nécessaires pour MongoDB Atlas) ---
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# --- Mettre pip à jour et installer les dépendances Python ---
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# --- Installer Chromium et ses dépendances Linux nécessaires ---
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    curl \
    unzip \
    fonts-liberation \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libxss1 \
    dos2unix \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# --- Convertir start.sh en format Unix et le rendre exécutable ---
RUN dos2unix /app/start.sh
RUN chmod +x /app/start.sh

# --- Variables d'environnement pour Chromium ---
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/lib/chromium/

# --- Commande pour démarrer le bot ---
CMD ["./start.sh"]
