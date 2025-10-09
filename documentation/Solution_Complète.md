# 🔐 Solution Complète — Pipeline Rescue

## Puzzle
- Réussite lorsque la mosaïque correspond exactement à data/poutine_bears.png.  
- OpenCV vérifie la différence < 0.05 → validation réussie.

## Analyse CSV
- Pipelines critiques : RU-0001 et RU-0002.  
- Capacités et années indiquent le site saboté : RU-0001.

## Scores IA
- KNN Regressor prédit RU-0001 avec score = 0.95 → très critique.  
- RU-0002 → 0.80.  
- Autres sites → < 0.50.

## Code final
- Site identifié : RU-0001.  
- Code secret : 5309.  
- API /final → { "site_code": "RU-0001", "code_a": "5309" } = "success"

## Communication
- Joueur 1 envoie CSV → Joueur 2.  
- Joueur 2 renvoie scores IA → Joueur 1.  
- Ensemble, ils postent via /validate, puis /final.