# 🧠 Documentation Technique — Pipeline Rescue

## 1. 🎯 Contexte du projet
**Pipeline Rescue : Opération Éco-Russie** est un escape game numérique éducatif à deux joueurs.  
Il combine logique, coopération et analyse de données industrielles simulées via une IA.

Le projet repose sur une architecture **FastAPI + Frontend HTML/JS** et inclut un système de **vérification d’images avec OpenCV**, un modèle **kNN prédictif** avec **scikit-learn**, et des interactions multijoueurs simulées.

---

## 2. 🏗️ Architecture technique

### Backend
- **FastAPI** : gestion des routes, logique métier et API REST
- **OpenCV** : découpe et vérification du puzzle image
- **Scikit-learn** : modèle d’apprentissage supervisé (kNN)
- **Joblib** : sauvegarde et chargement du modèle
- **Pandas** : lecture et manipulation du CSV industriel
- **Jinja2** : rendu des pages HTML côté serveur

### Frontend
- **HTML / CSS / JavaScript** : interface immersive et dynamique
- **joueur1.js / joueur2.js** : logique spécifique à chaque rôle
- **select_country.js / login.js** : gestion du flux narratif
- **Images statiques** : fonds de mission et indices visuels

### Structure simplifiée
```
projet-environnement/
│
├── backend/
│   ├── main.py
│   ├── routes/
│   ├── models/
│   └── utils/
├── frontend/
│   ├── static/js/
│   └── templates/
├── data/
│   ├── pipelines_ru.csv
│   └── mapping_codes.csv
└── tests/
```

---

## 3. ⚙️ Technologies utilisées

| Domaine | Technologie | Rôle principal |
|----------|--------------|----------------|
| API Backend | **FastAPI** | API REST + gestion du jeu |
| IA & Data | **scikit-learn**, **pandas**, **joblib** | Modèle de prédiction et gestion du CSV |
| Image | **OpenCV** | Vérification du puzzle image |
| Frontend | **HTML / CSS / JS / Jinja2** | Interface immersive |
| Tests | **pytest** | Tests unitaires et d’intégration |

---

## 4. 🧩 Principales fonctionnalités

1. **Puzzle image (authentification visuelle)**  
   - Vérification automatique de la solution avec OpenCV.  
   - Accès au CSV débloqué après réussite.

2. **Analyse de données industrielles (CSV)**  
   - Joueur 1 : manipulation du CSV des pipelines russes.  
   - Joueur 2 : modèle IA (kNN) pour prédire les scores.

3. **Validation croisée des scores**  
   - Synchronisation entre les joueurs pour détecter la fuite.

4. **Entrée du code final**  
   - Validation du code secret et fin de mission.

---

## 5. 🧠 Choix techniques clés

| Choix | Justification |
|--------|----------------|
| **FastAPI** | Rapidité, async, documentation auto, testabilité |
| **OpenCV** | Vérification fiable des images et puzzle interactif |
| **scikit-learn (kNN)** | Modèle simple, rapide, explicable |
| **pandas** | Lecture du CSV industriel et intégration IA |
| **pytest** | Tests automatisés garantissant la robustesse du jeu |
| **Jinja2 + JS** | Interface web narrative et immersive |

---

## 6. 🧩 Interactions principales (routes)

| Méthode | Endpoint | Description |
|----------|-----------|--------------|
| `GET` | `/puzzle/image` | Récupère l’image du puzzle |
| `POST` | `/puzzle/validate` | Vérifie la reconstitution correcte |
| `GET` | `/country/{code}` | Fournit le CSV selon le pays |
| `POST` | `/predict` | Lance le modèle IA sur les données |
| `POST` | `/validate` | Valide les scores saisis |
| `POST` | `/final` | Valide le code final de désactivation |
| `GET` | `/timer` | Retourne le temps restant |

---

## 7. 🧪 Système de tests

- **Pytest** est utilisé pour vérifier chaque route du backend.  
- Les tests sont regroupés en deux fichiers :  
  - `tests/pytest_joueur1.py`  
  - `tests/pytest_joueur2.py`  

Ces tests vérifient :
- le bon fonctionnement du puzzle,  
- la validation des données,  
- la cohérence des codes finaux,  
- et le rendu des pages HTML.

---

## 8. 🗂️ Données utilisées

- **pipelines_ru.csv** : contient les sites et leurs caractéristiques industrielles.
- **mapping_codes.csv** : relie chaque site à un code secret.
- **saved_scores.csv** : enregistre les scores soumis par le joueur 1.

---

## 9. 🚀 Lancement du projet

### Option 1 — Installation manuelle (classique)
```bash
git clone <repo>
cd projet-environnement
python -m venv venv
source venv/Scripts/activate      # (Windows)
# ou source venv/bin/activate     # (Linux/Mac)
pip install -r requirements.txt
python backend/main.py
```
Application disponible sur : [http://localhost:8000](http://localhost:8000)

---

### Option 2 — Installation automatisée (recommandée)

Le projet inclut un **script d’installation complet avec barre de progression** :  
> `setup.sh`

Ce script gère **toutes les étapes d’installation**, de la création du venv jusqu’au lancement automatique du serveur FastAPI.

#### Étapes effectuées automatiquement :
1. Création ou réutilisation de l’environnement virtuel  
2. Activation du venv  
3. Mise à jour de pip  
4. Nettoyage des versions conflictuelles d’OpenCV et Numpy  
5. Installation séquentielle des dépendances avec suivi visuel  
6. Barre de progression dynamique  
7. Démarrage automatique du serveur FastAPI  

#### Exécution :
Sous Linux ou macOS :
```bash
chmod +x setup.sh
./setup.sh
```
Sous Windows :
```bash
bash setup.sh
```
Le script affiche la progression et démarre le serveur automatiquement.

---

## 10. 🔒 Sécurité et authentification

- L’accès au CSV est bloqué tant que le puzzle n’est pas validé.  
- Les routes critiques utilisent des **en-têtes d’authentification** (`X-Auth-A`).  
- Les codes secrets sont **générés dynamiquement** et non stockés en clair.

---

## 11. 📈 Améliorations possibles

- Implémentation d’une vraie communication en temps réel via WebSockets.  
- Ajout d’un tableau de bord temps réel pour l’IA.  
- Version mobile optimisée.  
- Sauvegarde automatique des parties.

---

## 12. 👨‍💻 Auteurs
Développé par **Briac** — 2025  
Encadré par ChatGPT (modèle GPT-5) pour la structuration technique et les tests.
