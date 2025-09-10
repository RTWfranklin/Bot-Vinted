# --- Image de base Python slim ---
FROM python:3.11-slim

# --- Répertoire de travail ---
WORKDIR /app

# --- Copier les fichiers du projet ---
COPY . .

# --- Mettre pip à jour et installer les dépendances Python ---
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# --- Installer Chromium et ses dépendances pour Linux ---
RUN apt-get update && apt-get install -y \
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
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# --- Télécharger Chromium 140 portable (linux64) et le placer dans /usr/bin/chromium ---
RUN wget -q https://commondatastorage.googleapis.com/chromium-browser-snapshots/Linux_x64/140733981/chrome-linux.zip -O /tmp/chrome-linux.zip \
    && unzip /tmp/chrome-linux.zip -d /tmp \
    && mv /tmp/chrome-linux/chrome /usr/bin/chromium \
    && chmod +x /usr/bin/chromium \
    && rm -rf /tmp/chrome-linux /tmp/chrome-linux.zip

# --- S’assurer que start.sh est exécutable ---
RUN dos2unix start.sh
RUN chmod +x start.sh

# --- Commande pour démarrer le bot ---
CMD ["./start.sh"]
