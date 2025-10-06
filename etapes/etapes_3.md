🌐 ÉTAPE 3 — Routes backend (FastAPI)
Endpoint	Description	Fichier concerné
GET /country/{code}	Retourne le CSV complet (Joueur 1) ou amputé (Joueur 2) selon header	main.py
POST /predict	Prend les features (lat, lon, capacity, operator, year) et renvoie 3 noms + score de confiance	ia_model.py
POST /validate	Vérifie si les scores renvoyés sont cohérents	main.py
POST /final	Vérifie les codes simultanés 5309 et déverrouille la fin	main.py

🧩 Header d’authentification :

X-Auth-A: 7421   # Joueur 1
X-Auth-B: 8576   # Joueur 2
