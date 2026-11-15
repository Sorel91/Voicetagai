# VoiceTag AI

Prototype d'assistant personnel pour les réunions en présentiel.

## Lancer le prototype

Ouvrir `index.html` via un serveur local :

```bash
python3 -m http.server 8000
```

Puis ouvrir http://localhost:8000.

## Fonctionnalités actuellement disponibles

- Enregistrement audio dans le navigateur, avec export manuel du fichier
- Ajout et sélection manuelle des intervenants
- Notes horodatées, import de transcription et export TXT/JSON
- Compte rendu simple fondé sur des mots-clés

**Attention :** le prototype ne transcrit pas automatiquement les voix, ne reconnaît pas les personnes et n'utilise pas encore de LLM. L'audio n'est pas conservé après fermeture de la page.

## Architecture cible

- Frontend mobile web React / TypeScript
- API FastAPI pour les traitements audio
- faster-whisper pour la transcription
- pyannote.audio pour la diarisation
- Reconnaissance interactive et correction des intervenants
- LLM auto-hébergé pour les synthèses

## Confidentialité

Obtenir l'accord des participants avant l'enregistrement. Ne pas publier d'audios ou de transcriptions de réunions dans ce dépôt.

## Roadmap

1. Mesurer la diarisation sur des réunions tests consenties
2. Associer des segments vocaux aux personnes via des étiquettes manuelles
3. Propager les identifications avec un score de confiance et permettre les corrections
4. Générer des synthèses sourcées aux passages audio
5. Renforcer sécurité, stockage, tests et déploiement
