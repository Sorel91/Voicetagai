# Transcription locale — VoiceTag 0.2

Cette API utilise **faster-whisper** en local. Aucun service externe d'IA n'est requis.
Le premier lancement télécharge les poids du modèle (connexion Internet nécessaire à cette étape).

## Installation

Depuis la racine du dépôt :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Ouvrir http://127.0.0.1:8000 et autoriser le microphone.

Pour tester la transcription d'un fichier audio :

```bash
curl -F "audio=@exemple.wav" http://127.0.0.1:8000/api/transcribe
```

Réponse : `{"language":"fr","segments":[{"start":0.0,"end":1.2,"text":"Bonjour"}],"text":"Bonjour"}`.

Variables facultatives : `WHISPER_MODEL=small`, `WHISPER_DEVICE=cpu`, `WHISPER_COMPUTE_TYPE=int8`.
Le modèle `small` est un compromis pour le français ; pour une machine plus puissante, tester `medium`.

**Limites :** transcription après envoi du fichier, non temps réel ; pas de diarisation ni reconnaissance des personnes. Le serveur traite l'audio en mémoire et via un fichier temporaire supprimé à la fin. Les fichiers audio ne sont pas ajoutés au dépôt.

**Sécurité :** API à utiliser uniquement en local. Ne pas l'exposer sur Internet sans authentification, TLS, contrôles d'accès et durcissement. Ne pas traiter de réunions sans consentement.
