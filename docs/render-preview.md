# VoiceTag — prévisualisation protégée sur Render

La branche `deploy/render-preview` sert une prévisualisation accessible via HTTPS, protégée par authentification HTTP Basic.

## Configuration Render

- Runtime : Python
- Region : Frankfurt
- Branch : `deploy/render-preview`
- Build : `pip install -r backend/requirements-preview.txt`
- Start : `uvicorn backend.deployment:app --host 0.0.0.0 --port $PORT`
- Variables secrètes : `VOICETAG_USER` et `VOICETAG_PASSWORD`

L'URL `/health` reste publique pour les contrôles de disponibilité. Les autres routes nécessitent une authentification.

**Important :** ce déploiement léger est destiné à vérifier l'interface, l'enregistrement et les exports. Il n'installe **pas** les poids ni les dépendances lourdes de Whisper, pyannote et Resemblyzer : les endpoints IA ne sont pas fonctionnels tant qu'un serveur IA adapté n'a pas été déployé. Les modèles ne doivent pas être activés sur une offre insuffisante en RAM sans essais.

Le prototype n'a pas de comptes utilisateurs, d'anti-bruteforce ni de chiffrement des fichiers au repos ; ne pas y importer de réunions confidentielles. Les enregistrements envoyés aux endpoints existants sont traités en fichiers temporaires ; ne pas utiliser avec des données personnelles réelles sans audit de sécurité et validation RGPD.

Pour une mise en production, remplacer HTTP Basic par une véritable authentification, ajouter limites de requêtes et isolation des données, tests d'intégration et traitement asynchrone.
