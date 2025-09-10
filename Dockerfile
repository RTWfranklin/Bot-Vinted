# --- Image de base Python slim ---
FROM python:3.11-slim

# --- Répertoire de travail ---
WORKDIR /app

# --- Copier les fichiers du projet ---
COPY . .

# --- Installer certificats SSL et utilitaires ---
RUN echo "=== Installation des paquets system ===" \
    && apt-get update \
    && apt-get install -y \
        ca-certificates \
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
        dos2unix \
        --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && echo "=== Paquets system installés ==="

# --- Mettre pip à jour et installer les dépendances Python ---
RUN echo "=== Installation des packages Python ===" \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && echo "=== Packages Python installés ==="

# --- Convertir start.sh en format Unix et le rendre exécutable ---
RUN echo "=== Préparation du script start.sh ===" \
    && dos2unix /app/start.sh \
    && chmod +x /app/start.sh \
    && echo "=== Script prêt ==="

# --- Variables d'environnement pour Chromium ---
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/lib/chromium/

# --- Commande pour démarrer le bot avec log du démarrage ---
CMD echo "=== Démarrage du bot ===" && ./start.sh
