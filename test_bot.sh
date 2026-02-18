#!/bin/bash
# Script de test rapide du bot en local

echo "🔧 Test de l'environnement..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi
echo "✅ Python installé"

# Vérifier FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg n'est pas installé - Installation recommandée:"
    echo "   Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "   macOS: brew install ffmpeg"
    exit 1
fi
echo "✅ FFmpeg installé"

# Vérifier les variables d'environnement
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN non défini"
    echo "   Export avec: export TELEGRAM_BOT_TOKEN='votre_token'"
    exit 1
fi
echo "✅ TELEGRAM_BOT_TOKEN défini"

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY non défini"
    echo "   Export avec: export GEMINI_API_KEY='votre_cle'"
    exit 1
fi
echo "✅ GEMINI_API_KEY défini"

# Installer les dépendances
echo ""
echo "📦 Installation des dépendances Python..."
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dépendances installées"
else
    echo "❌ Erreur lors de l'installation"
    exit 1
fi

# Lancer le bot
echo ""
echo "🚀 Lancement du bot..."
echo "   Appuyez sur Ctrl+C pour arrêter"
echo ""
python3 telegram_shorts_bot.py
