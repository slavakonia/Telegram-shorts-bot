#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Telegram pour créer des Shorts Viraux automatiquement
Utilise Gemini AI (gratuit) + FFmpeg pour le traitement vidéo
"""

import os
import logging
import tempfile
import json
import asyncio
from datetime import datetime
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import whisper
import yt_dlp

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Configuration Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class ShortsGenerator:
    """Générateur de shorts viraux"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.whisper_model = None
    
    async def analyze_video_with_gemini(self, video_path):
        """Analyse la vidéo avec Gemini pour trouver les meilleurs moments"""
        try:
            # Upload video to Gemini
            video_file = genai.upload_file(video_path)
            
            prompt = """
            Analyse cette vidéo et identifie les 3-5 moments les plus viraux (30-60 secondes chacun).
            Pour chaque moment, fournis:
            
            1. Timestamp de début (en secondes)
            2. Timestamp de fin (en secondes)
            3. Titre accrocheur (max 100 caractères)
            4. Description virale (max 200 caractères)
            5. 10-15 hashtags pertinents
            6. Raison pour laquelle ce moment est viral
            7. Hook (première phrase pour capter l'attention)
            
            Réponds UNIQUEMENT en format JSON:
            {
                "clips": [
                    {
                        "start": 10.5,
                        "end": 45.2,
                        "title": "Titre accrocheur",
                        "description": "Description virale",
                        "tags": ["#viral", "#shorts", "#tendance"],
                        "hook": "Phrase d'accroche",
                        "viral_reason": "Pourquoi c'est viral"
                    }
                ]
            }
            
            Concentre-toi sur:
            - Moments émotionnels forts
            - Révélations surprenantes
            - Conseils pratiques rapides
            - Moments drôles/choquants
            - Transformations visuelles
            """
            
            response = self.model.generate_content([video_file, prompt])
            
            # Parse JSON response
            json_text = response.text.strip()
            if json_text.startswith('```json'):
                json_text = json_text[7:-3]
            elif json_text.startswith('```'):
                json_text = json_text[3:-3]
            
            analysis = json.loads(json_text)
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur analyse Gemini: {e}")
            return None
    
    def transcribe_audio(self, video_path):
        """Transcrit l'audio avec Whisper pour les sous-titres"""
        try:
            if self.whisper_model is None:
                self.whisper_model = whisper.load_model("base")
            
            result = self.whisper_model.transcribe(
                video_path,
                language='fr',
                word_timestamps=True
            )
            return result
            
        except Exception as e:
            logger.error(f"Erreur transcription: {e}")
            return None
    
    def create_short_with_subtitles(self, video_path, clip_info, transcription, output_path):
        """Crée un short avec sous-titres karaoké style"""
        try:
            # Charger la vidéo
            video = VideoFileClip(video_path).subclip(clip_info['start'], clip_info['end'])
            
            # Redimensionner en 9:16 (1080x1920)
            target_width = 1080
            target_height = 1920
            
            # Calculer le crop
            video_aspect = video.w / video.h
            target_aspect = target_width / target_height
            
            if video_aspect > target_aspect:
                # Vidéo trop large - crop horizontal
                new_width = int(video.h * target_aspect)
                x_center = video.w / 2
                x1 = int(x_center - new_width / 2)
                video = video.crop(x1=x1, width=new_width)
            else:
                # Vidéo trop haute - crop vertical
                new_height = int(video.w / target_aspect)
                y_center = video.h / 2
                y1 = int(y_center - new_height / 2)
                video = video.crop(y1=y1, height=new_height)
            
            # Redimensionner
            video = video.resize((target_width, target_height))
            
            # Ajouter les sous-titres karaoké
            subtitle_clips = []
            
            if transcription and 'segments' in transcription:
                for segment in transcription['segments']:
                    if segment['start'] >= clip_info['start'] and segment['end'] <= clip_info['end']:
                        text = segment['text'].strip()
                        start_time = segment['start'] - clip_info['start']
                        end_time = segment['end'] - clip_info['start']
                        
                        # Créer le sous-titre avec style karaoké
                        txt_clip = TextClip(
                            text,
                            fontsize=50,
                            color='white',
                            stroke_color='black',
                            stroke_width=3,
                            font='Arial-Bold',
                            method='caption',
                            size=(target_width - 100, None)
                        ).set_position(('center', 0.8), relative=True).set_start(start_time).set_duration(end_time - start_time)
                        
                        subtitle_clips.append(txt_clip)
            
            # Hook au début (3 premières secondes)
            if 'hook' in clip_info:
                hook_clip = TextClip(
                    clip_info['hook'],
                    fontsize=60,
                    color='yellow',
                    stroke_color='black',
                    stroke_width=4,
                    font='Arial-Bold',
                    method='caption',
                    size=(target_width - 100, None)
                ).set_position(('center', 0.15), relative=True).set_duration(3)
                
                subtitle_clips.append(hook_clip)
            
            # Composer la vidéo finale
            if subtitle_clips:
                final_video = CompositeVideoClip([video] + subtitle_clips)
            else:
                final_video = video
            
            # Export
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                threads=4
            )
            
            # Nettoyer
            video.close()
            final_video.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur création short: {e}")
            return False
    
    async def download_video(self, url, output_path):
        """Télécharge une vidéo depuis YouTube ou autre"""
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'outtmpl': output_path,
                'quiet': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur téléchargement: {e}")
            return False


# Instance globale
shorts_gen = ShortsGenerator()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /start"""
    welcome_text = """
🎬 **Bot Générateur de Shorts Viraux** 🚀

Je transforme vos vidéos longues en clips courts VIRAUX !

📱 **Fonctionnalités:**
✅ Analyse IA des meilleurs moments
✅ Format vertical 9:16 parfait
✅ Sous-titres karaoké animés
✅ Titres + descriptions + hashtags optimisés
✅ Clips de 30-60 secondes

📤 **Comment utiliser:**
1. Envoyez-moi une vidéo (fichier ou lien YouTube)
2. Je vais l'analyser avec Gemini AI
3. Vous recevrez 3-5 shorts prêts à publier !

🎯 **Commandes:**
/start - Voir ce message
/help - Aide détaillée

**Envoyez votre première vidéo maintenant ! 🎥**
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /help"""
    help_text = """
📚 **Guide d'utilisation**

**Formats acceptés:**
• Vidéo directe (fichier MP4, MOV, AVI)
• Lien YouTube
• Liens vidéo directs

**Processus:**
1️⃣ Envoi de votre vidéo
2️⃣ Analyse IA (~1-2 min)
3️⃣ Génération des shorts (~2-5 min)
4️⃣ Réception des clips + métadonnées

**Caractéristiques des shorts:**
📏 Durée: 30-60 secondes
📱 Format: 9:16 (vertical)
📝 Sous-titres: Style karaoké
🎯 Optimisé: TikTok, YouTube Shorts, Reels

**Astuce:** Les vidéos de 5-30 minutes donnent les meilleurs résultats !
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Traite une vidéo envoyée"""
    try:
        await update.message.reply_text("🎬 Vidéo reçue ! Traitement en cours...\n⏳ Cela peut prendre 5-10 minutes.")
        
        # Créer dossier temporaire
        temp_dir = tempfile.mkdtemp()
        input_video = os.path.join(temp_dir, 'input.mp4')
        
        # Télécharger la vidéo
        if update.message.video:
            file = await update.message.video.get_file()
            await file.download_to_drive(input_video)
        elif update.message.document:
            file = await update.message.document.get_file()
            await file.download_to_drive(input_video)
        
        # Analyse avec Gemini
        await update.message.reply_text("🤖 Analyse IA en cours avec Gemini...")
        analysis = await shorts_gen.analyze_video_with_gemini(input_video)
        
        if not analysis or 'clips' not in analysis:
            await update.message.reply_text("❌ Erreur lors de l'analyse. Réessayez avec une autre vidéo.")
            return
        
        await update.message.reply_text(f"✅ {len(analysis['clips'])} moments viraux détectés !\n🎬 Génération des shorts...")
        
        # Transcription audio
        await update.message.reply_text("🎤 Transcription audio pour sous-titres...")
        transcription = shorts_gen.transcribe_audio(input_video)
        
        # Créer chaque short
        for idx, clip_info in enumerate(analysis['clips'], 1):
            await update.message.reply_text(f"⚙️ Création du short {idx}/{len(analysis['clips'])}...")
            
            output_path = os.path.join(temp_dir, f'short_{idx}.mp4')
            
            success = shorts_gen.create_short_with_subtitles(
                input_video,
                clip_info,
                transcription,
                output_path
            )
            
            if success and os.path.exists(output_path):
                # Préparer les métadonnées
                caption = f"""
🎬 **Short #{idx}**

📌 **Titre:** {clip_info['title']}

📝 **Description:**
{clip_info['description']}

🏷️ **Tags:**
{' '.join(clip_info['tags'])}

💡 **Pourquoi viral:**
{clip_info.get('viral_reason', 'Moment fort identifié')}

⏱️ **Durée:** {clip_info['end'] - clip_info['start']:.1f}s
                """
                
                # Envoyer le short
                with open(output_path, 'rb') as video_file:
                    await update.message.reply_video(
                        video=video_file,
                        caption=caption,
                        parse_mode='Markdown',
                        supports_streaming=True
                    )
            else:
                await update.message.reply_text(f"❌ Erreur création short {idx}")
        
        await update.message.reply_text("✅ **Tous les shorts sont prêts !**\n🚀 Publiez-les sur TikTok, YouTube Shorts, Instagram Reels !")
        
        # Nettoyer
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        logger.error(f"Erreur traitement vidéo: {e}")
        await update.message.reply_text(f"❌ Erreur: {str(e)}\nRéessayez ou contactez le support.")


async def handle_youtube_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Traite un lien YouTube"""
    try:
        url = update.message.text
        await update.message.reply_text(f"📥 Téléchargement depuis YouTube...\n🔗 {url}")
        
        temp_dir = tempfile.mkdtemp()
        input_video = os.path.join(temp_dir, 'input.mp4')
        
        # Télécharger
        success = await shorts_gen.download_video(url, input_video)
        
        if not success or not os.path.exists(input_video):
            await update.message.reply_text("❌ Erreur téléchargement. Vérifiez le lien.")
            return
        
        await update.message.reply_text("✅ Vidéo téléchargée ! Traitement...")
        
        # Créer un objet message temporaire pour réutiliser handle_video
        # (On simule une vidéo uploadée)
        # Note: Cette partie nécessiterait plus de refactoring pour être propre
        
        await update.message.reply_text("🤖 Analyse IA en cours...")
        analysis = await shorts_gen.analyze_video_with_gemini(input_video)
        
        if not analysis or 'clips' not in analysis:
            await update.message.reply_text("❌ Erreur lors de l'analyse.")
            return
        
        await update.message.reply_text(f"✅ {len(analysis['clips'])} moments viraux !")
        
        transcription = shorts_gen.transcribe_audio(input_video)
        
        for idx, clip_info in enumerate(analysis['clips'], 1):
            await update.message.reply_text(f"⚙️ Short {idx}/{len(analysis['clips'])}...")
            
            output_path = os.path.join(temp_dir, f'short_{idx}.mp4')
            success = shorts_gen.create_short_with_subtitles(input_video, clip_info, transcription, output_path)
            
            if success:
                caption = f"""
🎬 **Short #{idx}**

📌 {clip_info['title']}

📝 {clip_info['description']}

🏷️ {' '.join(clip_info['tags'])}
                """
                
                with open(output_path, 'rb') as video_file:
                    await update.message.reply_video(video=video_file, caption=caption, parse_mode='Markdown')
        
        await update.message.reply_text("✅ Terminé !")
        
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        logger.error(f"Erreur YouTube: {e}")
        await update.message.reply_text(f"❌ Erreur: {str(e)}")


def main():
    """Démarre le bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN manquant !")
        return
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY manquant !")
        return
    
    # Créer l'application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_url))
    
    # Démarrer
    print("🤖 Bot démarré !")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
