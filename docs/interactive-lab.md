# Laboratoire interactif VoiceTag

La page **http://127.0.0.1:8000/speaker-lab** permet désormais d'essayer l'étiquetage d'un extrait de voix depuis le navigateur.

## Démarrer

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-speakers.txt
uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

1. Ouvrir `/speaker-lab` et choisir un enregistrement audio de réunion **consenti**.
2. Écouter et définir le début/la fin d'un passage de **2 secondes minimum**, avec une seule personne qui parle.
3. Entrer son nom, confirmer le consentement, cliquer sur **Associer cet extrait**.
4. Sélectionner un **autre** passage de cette même voix et cliquer sur **Reconnaître la voix sélectionnée**.
5. Refaire avec plusieurs personnes et des passages inconnus. Contrôler les erreurs et les refus.

L'extrait est converti en WAV mono dans le navigateur avant l'envoi au serveur local. Le serveur supprime son fichier temporaire après traitement ; il conserve seulement les empreintes vocales en mémoire. La page peut afficher les profils en mémoire et les effacer.

## Ce qui n'est PAS encore fait

- La sélection est manuelle ; pas de détection automatique des tours de parole.
- Pas d'apprentissage déclenché directement en touchant un prénom pendant une réunion en cours.
- Pas de reconnaissance entre redémarrages du serveur.
- Pas de mesures de qualité sur des voix réelles.
- L'API n'a pas d'authentification : ne jamais l'exposer publiquement.
- L'expérience peut échouer avec un extrait bruité, une voix qui chevauche une autre, ou un navigateur ne décodant pas le format.

## Critères pour l'étape suivante

Évaluer sur des enregistrements autorisés le taux de bonnes identifications, le taux de mauvaises identifications et les refus, avec des extraits provenant de différentes positions autour du téléphone. Les seuils doivent être calibrés avant de propager automatiquement des noms dans une réunion.
