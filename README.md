# 🎬 Bot Telegram - Générateur de Shorts Viraux

Transformez automatiquement vos vidéos longues en clips courts viraux avec IA !

## ✨ Fonctionnalités

- 🤖 **Analyse IA avec Gemini** : Détecte automatiquement les moments les plus viraux
- 📱 **Format 9:16** : Optimisé pour TikTok, YouTube Shorts, Instagram Reels
- 🎤 **Sous-titres Karaoké** : Sous-titres animés générés automatiquement
- 📝 **Métadonnées SEO** : Titres, descriptions et hashtags optimisés
- ⏱️ **Durée Optimale** : Clips de 30-60 secondes
- 🌐 **Support YouTube** : Téléchargement direct depuis YouTube

## 🚀 Déploiement Cloud GRATUIT

### Option 1 : Render.com (Recommandée)

1. **Créer un compte sur [Render.com](https://render.com)**

2. **Fork ce projet ou créez un nouveau repo GitHub** avec les fichiers fournis

3. **Sur Render Dashboard** :
   - Cliquez sur "New +" → "Web Service"
   - Connectez votre repo GitHub
   - Configuration :
     - **Environment** : Python 3.11
     - **Build Command** : `pip install -r requirements.txt && apt-get update && apt-get install -y ffmpeg`
     - **Start Command** : `python telegram_shorts_bot.py`
   
4. **Variables d'environnement** (dans Render) :
   - `TELEGRAM_BOT_TOKEN` : Votre token bot Telegram
   - `GEMINI_API_KEY` : Votre clé API Gemini

5. **Déployer** et c'est tout ! ✅

---

### Option 2 : Railway.app

1. **Créer un compte sur [Railway.app](https://railway.app)**

2. **New Project** → **Deploy from GitHub repo**

3. **Variables d'environnement** :
   ```
   TELEGRAM_BOT_TOKEN=votre_token
   GEMINI_API_KEY=votre_cle_api
   ```

4. **Railway va auto-détecter Python et installer les dépendances**

---

### Option 3 : Google Cloud Run (Plus technique)

```bash
# 1. Installer Google Cloud CLI
gcloud init

# 2. Créer un projet
gcloud projects create mon-bot-shorts

# 3. Déployer
gcloud run deploy shorts-bot \
  --source . \
  --platform managed \
  --region europe-west1 \
  --set-env-vars TELEGRAM_BOT_TOKEN=xxx,GEMINI_API_KEY=xxx
```

---

## 🔑 Obtenir les Clés API

### 1. Token Bot Telegram

1. Ouvrez Telegram et cherchez **@BotFather**
2. Envoyez `/newbot`
3. Suivez les instructions pour nommer votre bot
4. Copiez le token fourni (format : `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Clé API Gemini (GRATUIT)

1. Allez sur [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Cliquez sur "Get API Key"
3. Créez une nouvelle clé API
4. Copiez la clé (format : `AIzaSy...`)

**⚡ Quota gratuit Gemini** : 60 requêtes/minute - largement suffisant !

---

## 📱 Utilisation depuis votre Samsung A32

1. **Ouvrez Telegram** sur votre téléphone
2. **Cherchez votre bot** (le nom que vous avez donné)
3. **Envoyez `/start`**
4. **Envoyez une vidéo** :
   - Directement depuis votre galerie
   - Un lien YouTube
   - Un fichier vidéo

5. **Attendez 5-10 minutes**
6. **Recevez vos shorts** prêts à publier ! 🎉

---

## 📂 Structure des Fichiers

```
├── telegram_shorts_bot.py    # Code principal du bot
├── requirements.txt           # Dépendances Python
├── .env.example              # Exemple de configuration
├── README.md                 # Ce fichier
└── Dockerfile (optionnel)    # Pour Docker
```

---

## 🛠️ Installation Locale (Optionnel)

Si vous voulez tester localement avant le déploiement :

```bash
# 1. Cloner/créer le dossier
mkdir shorts-bot && cd shorts-bot

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Installer FFmpeg
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Windows: Télécharger depuis https://ffmpeg.org

# 4. Configurer les variables
cp .env.example .env
# Éditer .env avec vos clés

# 5. Lancer
python telegram_shorts_bot.py
```

---

## ⚙️ Configuration Avancée

### Personnaliser les sous-titres

Dans `telegram_shorts_bot.py`, ligne ~150 :

```python
txt_clip = TextClip(
    text,
    fontsize=50,           # Taille du texte
    color='white',         # Couleur (ou 'yellow', '#FF0000')
    stroke_color='black',  # Contour
    stroke_width=3,        # Épaisseur contour
    font='Arial-Bold',     # Police (Impact, Comic-Sans-MS, etc.)
)
```

### Modifier la durée des clips

Ligne ~50 dans le prompt Gemini :

```python
# Changer "30-60 secondes" par "45-90 secondes" par exemple
"identifie les 3-5 moments les plus viraux (45-90 secondes chacun)"
```

### Changer le nombre de clips générés

Ligne ~48 :

```python
# Changer "3-5 moments" par "5-10 moments"
"identifie les 5-10 moments les plus viraux"
```

---

## 🎯 Cas d'Usage

### 🎮 Gaming
- Extraire les meilleurs kills/plays
- Moments drôles/fails
- Tutoriels rapides

### 📚 Éducation
- Résumés de cours
- Tips & tricks
- Démonstrations

### 💼 Business
- Témoignages clients
- Conseils entrepreneurs
- Présentation produits

### 🎭 Divertissement
- Extraits podcast
- Bloopers
- Réactions

---

## 🐛 Dépannage

### Le bot ne répond pas
- Vérifiez que le service cloud est bien démarré
- Testez le token Telegram : `curl https://api.telegram.org/bot<TOKEN>/getMe`

### Erreur Gemini API
- Vérifiez votre quota : [Google AI Studio](https://makersuite.google.com)
- La clé API est-elle active ?

### Vidéos trop lourdes
- Limite Telegram : 50 MB par fichier
- Solution : Le bot compresse automatiquement

### Sous-titres manquants
- Vérifiez que l'audio est audible
- Whisper nécessite au moins 1 seconde d'audio

---

## 💡 Astuces Pro

1. **Vidéos de 5-30 min** = meilleurs résultats
2. **Contenu dynamique** = plus de clips détectés
3. **Audio clair** = meilleurs sous-titres
4. **Testez différentes niches** pour optimiser le prompt Gemini

---

## 📊 Limites Gratuites

| Service | Limite Gratuite |
|---------|----------------|
| Render.com | 750h/mois (suffisant pour bot 24/7) |
| Railway.app | $5 crédit/mois |
| Gemini API | 60 requêtes/min |
| Telegram Bot | Illimité |

---

## 🔄 Mises à Jour Futures

- [ ] Support multi-langues
- [ ] Templates de sous-titres prédéfinis
- [ ] Effets vidéo (zoom, transitions)
- [ ] Analyse des tendances TikTok
- [ ] Programmation publication automatique
- [ ] Statistiques de performance

---

## 📄 Licence

MIT License - Utilisez librement pour vos projets !

---

## 🤝 Support

Besoin d'aide ? 
- 📧 Email : support@example.com
- 💬 Telegram : @votre_support
- 🐛 Issues : GitHub Issues

---

## 🎉 Contributeurs

Créé avec ❤️ pour automatiser la création de contenu viral !

**Bon shortage ! 🚀📱**
