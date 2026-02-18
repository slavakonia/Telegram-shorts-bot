FROM python:3.11-slim

# Installer FFmpeg et dépendances système
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copier les fichiers
COPY requirements.txt .
COPY telegram_shorts_bot.py .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Variables d'environnement (à surcharger au déploiement)
ENV TELEGRAM_BOT_TOKEN=""
ENV GEMINI_API_KEY=""

# Commande de démarrage
CMD ["python", "telegram_shorts_bot.py"]
