# 🛰️ Guide du Joueur 2 — Pipeline Rescue

Bienvenue agent ! 🎯
Tu es le **Joueur 2**, analyste IA. Tu aides le Joueur 1 à interpréter les données et à identifier le pipeline compromis.

## Rôle et Objectifs
- Consulter les scores de confiance produits par le KNN Regressor.  
- Comparer les prédictions IA avec les informations du CSV fourni par Joueur 1.  
- Conseiller le Joueur 1 sur les pipelines les plus suspects.  
- Valider les scores côté API pour identifier le site compromis.  
- Saisir le code final pour sécuriser le pipeline.

## Déroulement détaillé
1. **Connexion** : /login → sélection du pays (Russie).  
2. **Observation** : visualise l'image du puzzle reconstituée par Joueur 1.  
3. **Analyse IA** : appelle l’API /predict pour chaque pipeline reçu.  
4. **Communication** : envoie les scores et suggestions au Joueur 1.  
5. **Validation** : poste les scores corrigés via /validate.  
6. **Finalisation** : quand le pipeline est identifié, récupère le code secret et poste-le via /final.

## Astuces
- Vérifie que les prédictions sont cohérentes avec les informations CSV.  
- Attention au timer : 30 min, pénalités de 5 min si incohérence.  
- Coordonne avec Joueur 1 : la réussite dépend de la coopération.