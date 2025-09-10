# --- Image de base Python Debian complète ---
FROM python:3.11-bullseye

WORKDIR /app
COPY . .

# --- Installer certificats SSL et dépendances pour TLS + Chromium ---
RUN apt-get update && apt-get install -y \
    ca-certificates \
    openssl \
    libssl-dev \
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

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN dos2unix /app/start.sh
RUN chmod +x /app/start.sh

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/lib/chromium/

CMD ["./start.sh"]
