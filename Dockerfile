# --- Image de base ---
FROM python:3.11-slim

# --- Répertoire de travail ---
WORKDIR /app

# --- Copier tout le projet ---
COPY . .

# --- Mettre à jour pip et installer les dépendances ---
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
    libgconf-2-4 \
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
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# --- Donner les permissions d'exécution à start.sh ---
RUN chmod +x start.sh

# --- Commande pour lancer le bot ---
CMD ["./start.sh"]
