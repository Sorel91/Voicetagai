# VoiceTag — première analyse IA intégrée (prototype)

Cette version combine **faster-whisper** (transcription) et **pyannote** (diarisation), puis rapproche leurs segments par chevauchement temporel. Elle utilise facultativement les empreintes vocales enregistrées en mémoire par le laboratoire des voix pour proposer des noms.

## Installation locale

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-diarization.txt
export HF_TOKEN='votre_token_huggingface'
uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

**Prérequis :** accepter les conditions d'accès du modèle `pyannote/speaker-diarization-3.1` et ses dépendances sur Hugging Face ; utiliser un token avec permissions minimales. Les modèles téléchargent des poids au premier lancement. Ne jamais commiter le token.

Ouvrir **http://127.0.0.1:8000/meeting-analysis**.

1. Préparer un fichier WAV de réunion de moins de 30 Mo, enregistré avec le consentement des personnes.
2. Facultatif : visiter `/speaker-lab` pour apprendre des voix sur des extraits isolés. Les profils sont seulement en mémoire du processus.
3. Importer le WAV et cliquer sur **Analyser avec l'IA**.
4. Corriger les noms proposés dans la liste des intervenants. Une correction est appliquée à tous les segments partageant le même identifiant anonyme.
5. Exporter le JSON ou le TXT corrigé.

API : `POST /api/analyze-meeting` avec un champ multipart `audio=@reunion.wav`.

## Limites actuelles

- **Aucun test de bout en bout sur un vrai audio n'a été effectué.** La compatibilité des modèles et leurs performances restent à vérifier.
- Attribution par chevauchement temporel : ce n'est **pas** un alignement précis des mots. Les segments traversant un changement d'intervenant peuvent être mal attribués ou laissés sans nom.
- Les corrections faites dans la page **n'entraînent pas encore** les empreintes vocales. Le laboratoire de voix permet un enrôlement séparé.
- Pas de streaming, pas de capture iPhone intégrée à cette page, pas de persistance des profils, pas de résumé LLM.
- La page ne conserve pas les corrections après rechargement, sauf export manuel.
- API sans authentification, **strictement locale**. Aucune exposition Internet avant durcissement, RGPD et tests.
- En cas de voix superposées, d'acoustique difficile ou de microphone distant, la fiabilité peut être faible.

## Validation à faire avant fusion

- Lancer les tests CI et les tests d'intégration sur machine disposant des modèles.
- Vérifier une réunion consentie avec 2, 3 puis 4 intervenants.
- Mesurer les erreurs d'attribution et les refus, comparer avec une annotation humaine.
- Tester les imports WAV, fichiers volumineux, fichiers corrompus et suppression des fichiers temporaires.
