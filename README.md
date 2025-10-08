# 🛰️ Pipeline Rescue : Opération Éco-Russie

### 🎮 Escape Game Numérique Éducatif

Deux agents du gouvernement doivent empêcher l’explosion d’un pipeline russe saboté.  
Entre puzzle miroir, données industrielles et intelligence artificielle, la mission exige coopération, analyse et rapidité.

---

## 🎯 Objectifs pédagogiques
- Sensibiliser aux risques écologiques et à la dépendance au pétrole.  
- Illustrer le rôle de l’IA dans la gestion de données industrielles.  
- Promouvoir la coopération et la communication efficace entre joueurs.

---

## 🧩 Fonctionnement du jeu

1. **Découverte de la lettre**  
   - Accéder au portail sécurisé.

2. **Choix du pays**  
   - 4 pays simulés : Inde, Russie, Australie, USA.  
   - Seule la Russie contient de vraies données.

3. **Authentification (Puzzle 3D)**  
   - Chaque face du puzzle donne un code (keep / calm).  
   - Le code définit le rôle : Joueur 1 (complet) / Joueur 2 (IA).

4. **Puzzle avec image** 
   - le joueur 1 a un puzzle avec 9 morceau d'une image ( image couper en 9 de facon uniforme)
   - le joueur 2 a l'image que le joueur 1 doit reconstiituer 

   - le joueur un deplace les morceaux d'image pour creer la bonne image 
   - on utilise opencv pour verifier que l'image correspond bien a l'imge de base 
   - Si l'image est bonne alors on ouvre le csv 

5. **Manipulation de données**  
   - Joueur 1 → CSV des pipelines.  
   - Joueur 2 → Console IA prédictive (modèle kNN).  
   - Ensemble, ils complètent les scores de confiance et identifient la fuite.
   - si tout le tableau est remplis et juste alors un message avec le code apparrait et le nom du pipeline 

6. **Coupure du pipeline**  
   - Entrée seul du code `5309`.  
   - Succès → fuite évitée / Échec → explosion virtuelle.

7. **Révélation finale**  
   - Message :  
     > “Mission accomplie. Le pétrole aussi.  
     > La vraie mission, c’est de trouver des solutions durables.”

---
