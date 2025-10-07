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
   - Trouver le code miroir dans le texte (“Cher camarade”).  
   - Accéder au portail sécurisé.

2. **Authentification (Puzzle 3D)**  
   - Chaque face du puzzle donne un code (7421 / 8576).  
   - Le code définit le rôle : Joueur 1 (complet) / Joueur 2 (IA).

3. **Choix du pays**  
   - 4 pays simulés : Inde, Russie, Australie, USA.  
   - Seule la Russie contient de vraies données.

4. **Manipulation de données**  
   - Joueur 1 → CSV des pipelines.  
   - Joueur 2 → Console IA prédictive (modèle kNN).  
   - Ensemble, ils complètent les scores de confiance et identifient la fuite.

5. **Coupure du pipeline**  
   - Entrée simultanée du code `5309`.  
   - Succès → fuite évitée / Échec → explosion virtuelle.

6. **Révélation finale**  
   - Message :  
     > “Mission accomplie. Le pétrole aussi.  
     > La vraie mission, c’est de trouver des solutions durables.”

---

## 🧠 Technologies utilisées
| Composant | Technologie |
|------------|-------------|
| Frontend | React.js |
| Backend | FastAPI |
| IA Prédictive | Python (scikit-learn, kNN) |
| Données | CSV open data (OpenStreetMap / GEM) |
| Communication | WebSocket (Socket.IO) |
| Authentification | Codes miroir |

---

## 📂 Structure du projet




## Données utilisées

Les fichiers CSV de ce projet (`pipelines_ru.csv`, `pipelines_ru_cut.csv`, `mapping_codes.csv`) ont été créés à partir de données **synthétiques et anonymisées**.

Ils s’inspirent de sources ouvertes :
- Global Energy Monitor – Global Oil & Gas Pipeline Tracker  
  [https://globalenergymonitor.org/projects/global-oil-gas-pipeline-tracker/](https://globalenergymonitor.org/projects/global-oil-gas-pipeline-tracker/)
- OpenStreetMap (pipeline=oil/gas)
  [https://www.openstreetmap.org](https://www.openstreetmap.org)
- Wikipédia – Liste d’entreprises pétrolières russes  
  [https://fr.wikipedia.org/wiki/Liste_d%27entreprises_p%C3%A9troli%C3%A8res](https://fr.wikipedia.org/wiki/Liste_d%27entreprises_p%C3%A9troli%C3%A8res)

> ⚠️ Ces données sont fictives, à usage pédagogique dans le cadre du projet *Pipeline Rescue : Opération Éco-Russie*.

🗂️ Sources ouvertes utilisées comme référence
Domaine	Source	Description	Lien
Pipelines mondiaux	Global Energy Monitor – Global Oil & Gas Pipeline Tracker	Base de données collaborative recensant les pipelines mondiaux (dont la Russie).	🌍 https://globalenergymonitor.org/projects/global-oil-gas-pipeline-tracker/

Réseaux énergétiques russes	OpenStreetMap (tag pipeline=oil ou pipeline=gas)	Données géographiques ouvertes sur les infrastructures énergétiques.	🗺️ https://www.openstreetmap.org

Entreprises opératrices	Wikipédia – Liste des compagnies pétrolières russes (Gazprom, Rosneft, Lukoil, etc.)	Références pour les noms d’opérateurs plausibles.	📘 https://fr.wikipedia.org/wiki/Liste_d%27entreprises_p%C3%A9troli%C3%A8res





🛰️ README — Pipeline Rescue : Opération Éco-Russie

(Version complète – prête pour GitHub)

🧭 Présentation

Pipeline Rescue : Opération Éco-Russie est un escape game numérique coopératif à visée éducative et environnementale.
Deux agents du gouvernement doivent empêcher l’explosion d’un pipeline russe saboté en utilisant l’intelligence artificielle et la coopération en temps réel.

🕹️ Durée moyenne : 30–45 minutes
👥 Joueurs : 2 (coopératif – rôles asymétriques)
🎓 Public cible : Lycéens (15–18 ans)
🌍 Thème : Environnement, écologie industrielle, dépendance au pétrole

🎯 Objectifs pédagogiques

Sensibiliser aux risques écologiques et à la dépendance énergétique.

Découvrir le rôle de l’IA dans la gestion des données industrielles.

Encourager la collaboration et la communication entre deux agents aux accès différents.

🧩 Synopsis

Un sabotage numérique a visé un pipeline pétrolier russe.
Deux agents d’intervention — Joueur 1 et Joueur 2 — doivent identifier la fuite, analyser des données industrielles corrompues, et activer la coupure d’urgence avant l’explosion.

💬 “Cher camarade... La mission commence dans le reflet.”
Un code en miroir, un puzzle 3D et une IA cachée dans les serveurs russes seront vos seules armes.

💻 Technologies utilisées
Composant	Technologie
Frontend	React.js
Backend	FastAPI (Python)
IA Prédictive	scikit-learn (modèle kNN)
Données	CSV (OpenStreetMap / GEM synthétisées)
Communication	WebSocket (Socket.IO)
Authentification	Codes miroir gravés (7421 / 8576)
📂 Structure du projet
pipeline-rescue/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── assets/
│   │   └── App.jsx
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── models/
│   │   └── ia_model.py
│   ├── utils/
│   │   └── loader.py
│   └── data/
│       ├── pipelines_ru.csv
│       ├── pipelines_ru_cut.csv
│       ├── pipelines_in.csv
│       ├── pipelines_au.csv
│       └── pipelines_us.csv
│
├── docs/
│   ├── README.md
│   ├── rapport-technique.pdf
│   └── poster-A3.pdf
│
└── assets/
    ├── lettre_cher_camarade.png
    ├── puzzle_3D.svg
    └── mockups-ui.png

⚙️ Installation & Lancement
1️⃣ Backend (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

2️⃣ Frontend (React)
cd frontend
npm install
npm run dev

3️⃣ Lancement global

Ouvrir deux onglets navigateur :

localhost:5173 → Interface Joueur 1

localhost:5173?role=ai → Interface Joueur 2

🧠 Fonctionnement du jeu (résumé)
Étape	Description	Code clé
1️⃣ Lettre miroir	Trouver le code “Cher camarade”	123
2️⃣ Puzzle 3D	Décoder les deux faces miroir	7421 / 8576
3️⃣ Authentification	Choisir le pays (Russie = vrai)	—
4️⃣ Données CSV + IA	IA kNN pour détecter la fuite	—
5️⃣ Coupure simultanée	Entrée double du code final	5309
🧩 Données utilisées

Fichiers CSV fictifs inspirés de données ouvertes :

Global Energy Monitor (GEM)

OpenStreetMap (tag pipeline=oil/gas)

Wikipédia – entreprises pétrolières russes

⚠️ Données synthétiques, à usage pédagogique uniquement.

🎨 Direction artistique (DA)

Univers visuel : salle de contrôle soviétique (interface rouge/noire, typographie numérique).

Effets sonores : alarme, cliquetis d’ordinateurs, voix IA.

Ambiance : tension, coopération, compte à rebours.

Symbolique : le “miroir” = double lecture, éthique et données falsifiées.

👥 Équipe & Crédits
Nom	Rôle	Contribution
[Ton nom]	Chef de projet / Dev IA	Architecture, IA kNN, backend
[Coéquipier]	Frontend Dev	Interface React + WebSocket
[Coéquipier]	Designer	DA, puzzle, assets
[Coéquipier]	Game designer	Énigmes, narration, pédagogie
📜 Licence

Projet réalisé dans le cadre du Workshop M1 EPSI/WIS 2025–2026 :

“Escape Tech : Crée ton aventure numérique”






🛰️ Pipeline Rescue : Opération Éco-Russie
🎮 Escape Game Numérique Éducatif

Deux agents du gouvernement doivent empêcher l’explosion d’un pipeline russe saboté.
Entre puzzle miroir, données industrielles et intelligence artificielle, la mission exige coopération, analyse et rapidité.

🎯 Objectifs pédagogiques

Sensibiliser aux risques écologiques et à la dépendance au pétrole.

Illustrer le rôle de l’IA dans la gestion de données industrielles.

Promouvoir la coopération et la communication efficace entre joueurs.

🧭 Présentation générale

Pipeline Rescue : Opération Éco-Russie est un escape game numérique coopératif à visée éducative et environnementale.
Deux agents du gouvernement doivent identifier la fuite d’un pipeline russe saboté en utilisant une IA prédictive et en collaborant sous pression.

🕹️ Durée moyenne : 30–45 minutes

👥 Joueurs : 2 (coopératif – rôles asymétriques)

🎓 Public cible : Lycéens (15–18 ans)

🌍 Thème : Environnement, écologie industrielle, dépendance énergétique

🧩 Fonctionnement du jeu

Découverte de la lettre — lettre commençant par “Cher camarade…”, code miroir (123) pour accéder au portail.

Authentification (Puzzle 3D) — deux codes : 7421 / 8576 (définit Joueur 1 / Joueur 2).

Choix du pays — Inde / Russie / Australie / USA (seule la Russie contient les données réelles).

Manipulation de données — Joueur 1 : CSV ; Joueur 2 : console IA (kNN) → compléter confidence_score.

Coupure du pipeline — entrée simultanée du code 5309. Succès = fuite évitée.

Révélation finale — message final pédagogique sur la durabilité.

“Mission accomplie. Le pétrole aussi.
La vraie mission, c’est de trouver des solutions durables.”

🧠 Technologies utilisées
Composant	Technologie
Frontend	React.js
Backend	FastAPI (Python)
IA Prédictive	scikit-learn (kNN)
Données	CSV (OpenStreetMap / Global Energy Monitor synthétisées)
Communication	WebSocket (Socket.IO)
Authentification	Codes miroir (7421 / 8576)
📂 Structure du projet
pipeline-rescue/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── assets/
│   │   └── App.jsx
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── models/
│   │   └── ia_model.py
│   ├── utils/
│   │   └── loader.py
│   └── data/
│       ├── pipelines_ru.csv
│       ├── pipelines_ru_cut.csv
│       ├── pipelines_in.csv
│       ├── pipelines_au.csv
│       └── pipelines_us.csv
│
├── docs/
│   ├── README.md
│   ├── rapport-technique.pdf
│   └── poster-A3.pdf
│
└── assets/
    ├── lettre_cher_camarade.png
    ├── puzzle_3D.svg
    └── mockups-ui.png

⚙️ Installation & Lancement
Backend (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

Frontend (React)
cd frontend
npm install
npm run dev

Lancement global

http://localhost:5173 → Interface Joueur 1

http://localhost:5173?role=ai → Interface Joueur 2

🧠 Fonctionnement — résumé des codes
Étape	Description	Code clé
1️⃣	Lettre miroir	123
2️⃣	Puzzle 3D (auth)	7421 / 8576
3️⃣	Choix du pays (Russie = vrai)	—
4️⃣	CSV + IA (kNN)	—
5️⃣	Coupure finale (simultanée)	5309
📊 Données utilisées

Ces données sont fictives, à usage pédagogique dans le cadre du projet Pipeline Rescue : Opération Éco-Russie.

🗂️ Sources ouvertes utilisées comme référence

Domaine	Source	Description	Lien
Pipelines mondiaux	Global Energy Monitor – Global Oil & Gas Pipeline Tracker	Base de données collaborative recensant les pipelines mondiaux (dont la Russie).	🌍 https://globalenergymonitor.org/projects/global-oil-gas-pipeline-tracker/

Réseaux énergétiques russes	OpenStreetMap (tag pipeline=oil ou pipeline=gas)	Données géographiques ouvertes sur les infrastructures énergétiques.	🗺️ https://www.openstreetmap.org

Entreprises opératrices	Wikipédia – Liste des compagnies pétrolières russes (Gazprom, Rosneft, Lukoil, etc.)	Références pour les noms d’opérateurs plausibles.	📘 https://fr.wikipedia.org/wiki/Liste_d%27entreprises_p%C3%A9troli%C3%A8res

⚠️ Remarque : tous les CSV du dépôt (pipelines_ru.csv, pipelines_ru_cut.csv, mapping_codes.csv) sont synthétiques et anonymisés à des fins pédagogiques.

🎨 Direction artistique (DA)

Univers visuel : salle de contrôle soviétique — palette rouge / gris / vert.

Ambiance sonore : alarmes, voix IA, bruits industriels.

Symbolique : le miroir (vérité inversée, données falsifiées).

Typographie / UI : police monospace / style terminal pour renforcer l’atmosphère.

🧩 Plan de création — énigmes, indices et codes (résumé)

DA & fil narratif — définir textes, palette, sons.

Énigme 1 (Lettre miroir) — créer texte bilingue / miroir → code 123.

Énigme 2 (Puzzle 3D) — fabriquer / modéliser puzzle → codes 7421 / 8576.

Énigme 3 (CSV saboté) — préparer pipelines_ru.csv + pipelines_ru_cut.csv ; implémenter ia_model.py (kNN).

Énigme 4 (Coupure simultanée) — Socket.IO, timer 30s, code 5309.

Débrief — modal pédagogique et scoring.

🧱 Chronologie de production (4 jours recommandés)
Jour	Objectifs
Jour 1	DA, lettre miroir (123)
Jour 2	Puzzle 3D + authentification (7421 / 8576)
Jour 3	Données + IA (kNN)
Jour 4	Coupure finale (5309) + débrief
👥 Équipe & Crédits
Nom	Rôle
[Ton Nom]	Chef de projet / Dev IA
[Coéquipier 1]	Frontend Dev
[Coéquipier 2]	Designer / DA
[Coéquipier 3]	Game Designer
📜 Licence

Projet réalisé dans le cadre du Workshop M1 EPSI / WIS 2025–2026 — Escape Tech : Crée ton aventure numérique.
© Pipeline Rescue Team — Usage pédagogique uniquement.


