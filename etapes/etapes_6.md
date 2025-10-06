
💬 ÉTAPE 6 — Interface joueur (React)
Écran 1 : Choix du pays (carte interactive → clic Russie)

Écran 2 : Interface CSV (Joueur 1) et Console IA (Joueur 2)

Écran 3 : Validation + alerte fuite

Écran 4 : Coupure simultanée (code 5309 → success/fail)

Écran 5 : Message final écologique

💡 Les deux écrans sont synchronisés par Socket.IO :

js
Copier le code
socket.emit("validation", { code: "5309" });

