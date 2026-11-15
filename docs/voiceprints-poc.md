# PoC VoiceTag — reconnaissance d'une voix pré-étiquetée

**Statut : expérimental, non validé en conditions réelles.**

Cette étape teste si un clip contenant **une seule voix** peut être associé à un participant préalablement identifié. Elle ne sépare **pas** les intervenants d'une réunion complète et n'est **pas** une reconnaissance en direct.

## Lancement

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-speakers.txt
uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Le premier appel peut télécharger des poids de modèle. Garder l'API accessible uniquement sur localhost.

## Enrôler une voix

Préparer un extrait de 3 à 10 secondes où Jonathan parle seul, avec son consentement.

```bash
curl -F 'name=Jonathan' -F 'consent=true' -F 'audio=@jonathan.wav' http://127.0.0.1:8000/api/speakers/enroll
```

Recommencer avec Ahmed, puis comparer un nouvel extrait :

```bash
curl -F 'audio=@inconnu.wav' http://127.0.0.1:8000/api/speakers/identify
```

Une réponse `speaker: null` signifie **inconnu ou incertain**, pas une erreur. Les scores ne sont **pas** des probabilités calibrées. Les seuils 0.78 / 0.06 sont des hypothèses à évaluer, pas une garantie de précision.

Supprimer un profil :

```bash
curl -X DELETE http://127.0.0.1:8000/api/speakers/Jonathan
```

Supprimer tous les profils :

```bash
curl -X DELETE http://127.0.0.1:8000/api/speakers
```

## Limites et sécurité

- Les embeddings biométriques restent en mémoire du processus, disparaissent au redémarrage et ne sont pas persistés.
- Les extraits audio temporaires sont supprimés après analyse.
- Aucun stockage durable ni reconnaissance entre sessions.
- Aucun endpoint ne doit être exposé publiquement : **pas d'authentification**, pas de chiffrement applicatif ni de cloisonnement par utilisateur.
- Les résultats sont sensibles au bruit, au micro, à la distance et au chevauchement des voix.
- Les embeddings vocaux peuvent constituer des données biométriques sensibles : réaliser une analyse RGPD et obtenir un consentement explicite et valable avant de tester avec de vraies personnes.
- Prochaine étape : diarisation / découpage de la réunion, UI d'attribution, propagation contrôlée et protocole de mesure (taux de fausses attributions et de rejets).
