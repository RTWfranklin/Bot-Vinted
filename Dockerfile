# --- Image de base ---
FROM python:3.11-slim

# --- Répertoire de travail ---
WORKDIR /app

# --- Copier les fichiers du projet ---
COPY . .

# --- Installer pip et dépendances Python ---
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install selenium webdriver-manager

# --- Installer Chromium et dépendances nécessaires ---
RUN apt-get update && apt-get install -y \
    chromium \
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

# --- Rendre start.sh exécutable ---
RUN chmod +x start.sh

# --- Commande pour démarrer le bot ---
CMD ["./start.sh"]
