# 🎮 Guide du Joueur 1 — Pipeline Rescue

Bienvenue agent ! 🎯
Tu es le **Joueur 1**, maître du terrain et gardien des données. Ta mission est de protéger le pipeline russe saboté.

## Rôle et Objectifs
- Reconstituer le puzzle image pour débloquer l’accès aux données.
- Analyser le CSV des pipelines (data/pipelines_ru.csv).
- Communiquer avec le Joueur 2 pour valider les scores et identifier le pipeline compromis.
- Valider le code final une fois le pipeline identifié.

## Déroulement détaillé
1. **Connexion** : ouvre le navigateur → /login → sélectionne la Russie.  
2. **Puzzle image** : déplace les 9 morceaux pour reconstituer l’image.  
   - OpenCV valide la reconstruction (95% similarity).  
3. **Accès CSV** : le puzzle correct ouvre le fichier pipelines_ru.csv.  
4. **Analyse des données** : note la capacité, localisation et année des pipelines.  
5. **Communication avec Joueur 2** :  
   - Transmets les informations brutes.  
   - Reçois les scores IA pour chaque site.  
6. **Validation** : remplis la table de scores côté API → /validate.  
7. **Code final** : quand le pipeline est identifié, récupère le code secret et envoie-le via /final.

## Astuces
- Utilise la logique et la comparaison entre le CSV et les prédictions IA.  
- Attention au timer : 30 min, pénalités de 5 min si erreurs.  
- Communique efficacement avec le Joueur 2 pour gagner du temps.