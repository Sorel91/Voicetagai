# VoiceTag — diarisation expérimentale

La diarisation consiste à repérer **qui parle quand**, même lorsque les noms ne sont pas connus. L'API locale `POST /api/diarize` renvoie des segments horodatés avec des identifiants `SPEAKER_00`, etc. Lorsque des empreintes vocales ont été enregistrées avec `/api/speakers/enroll`, le serveur peut **proposer** des noms.

## Préparation

1. Créer un compte Hugging Face et accepter les conditions d'accès du modèle `pyannote/speaker-diarization-3.1` ainsi que de ses dépendances éventuellement soumises à autorisation.
2. Créer un token Hugging Face limité aux permissions nécessaires ; ne **jamais** le commiter dans GitHub.
3. Installer les dépendances, puis lancer l'API **sur localhost** :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-diarization.txt
export HF_TOKEN='votre_token'
uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

4. Avec un enregistrement WAV consenti :

```bash
curl -F 'audio=@reunion.wav' http://127.0.0.1:8000/api/diarize
```

## Format de réponse

```json
{
  "segments": [
    {"start": 0.8, "end": 4.1, "speaker_id": "SPEAKER_00", "name": null},
    {"start": 4.4, "end": 7.2, "speaker_id": "SPEAKER_01", "name": "Ahmed"}
  ],
  "speakers": {
    "SPEAKER_00": {"name": null, "status": "uncertain"},
    "SPEAKER_01": {"name": "Ahmed", "status": "proposed"}
  },
  "speaker_count": 2,
  "method": "pyannote/speaker-diarization-3.1",
  "warning": "Noms proposés automatiquement, à vérifier avant diffusion."
}
```

## Précautions

- Cette étape est un **PoC non testé sur de vrais enregistrements**.
- L'API ne fournit pas encore le texte de transcription aligné avec les tours de parole. Il faudra rapprocher les segments de faster-whisper et ceux de pyannote.
- Les propositions de noms ne sont faites qu'avec au moins **deux clips distincts**, sans chevauchement, ayant obtenu la même reconnaissance.
- Les seuils de similarité sont expérimentaux ; pas de précision mesurée.
- Le modèle peut nécessiter des ressources matérielles significatives et télécharger des poids à la première utilisation.
- Le token est secret ; ne jamais le stocker dans le dépôt.
- La sortie doit être revue avant tout compte rendu ; aucun résultat ne doit être présenté comme une identification certaine.
- Usage local uniquement, avec consentement et analyse RGPD appropriée pour les données vocales.
