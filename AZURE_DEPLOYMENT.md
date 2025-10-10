# Guide de Déploiement Azure - Correction du Compteur

## Problème Identifié

Le compteur ne fonctionne plus sur Azure à cause de plusieurs problèmes :

1. **Endpoint `/timer/start` manquant** ✅ **CORRIGÉ**
2. **Configuration WebSocket incorrecte pour Azure** ✅ **CORRIGÉ**
3. **Problèmes de protocole HTTPS/WSS** ✅ **CORRIGÉ**

## Solutions Implémentées

### 1. Endpoint Timer Manquant
- ✅ Ajouté l'endpoint `POST /timer/start` dans `backend/routes/backend_routes.py`
- ✅ L'endpoint démarre le timer côté serveur

### 2. Configuration WebSocket pour Azure
- ✅ Correction de la logique de protocole WebSocket
- ✅ Support automatique de `wss://` pour HTTPS
- ✅ Fallback automatique vers `ws://` si `wss://` échoue
- ✅ Gestion des erreurs de connexion améliorée

### 3. Configuration Azure Spécialisée
- ✅ Fichier `azure_config.py` pour la configuration Azure
- ✅ Fichier `web.config` pour IIS sur Azure
- ✅ Script de démarrage `start_azure.py` optimisé
- ✅ Configuration CORS adaptée pour Azure

## Fichiers Modifiés

### Backend
- `backend/routes/backend_routes.py` - Ajout endpoint `/timer/start`
- `backend/main.py` - Configuration Azure et CORS

### Frontend
- `frontend/static/js/joueur1.js` - Correction WebSocket et fallback
- `frontend/static/js/joueur2.js` - Correction WebSocket et fallback

### Nouveaux Fichiers
- `azure_config.py` - Configuration Azure
- `start_azure.py` - Script de démarrage Azure
- `web.config` - Configuration IIS pour Azure
- `test_azure_websocket.py` - Script de diagnostic
- `AZURE_DEPLOYMENT.md` - Ce guide

## Instructions de Déploiement

### 1. Préparer le Déploiement
```bash
# Installer les dépendances
pip install -r requirements.txt

# Tester localement
python start_azure.py
```

### 2. Déployer sur Azure
1. **Créer une App Service** sur Azure Portal
2. **Configurer Python 3.9** comme runtime
3. **Déployer le code** via Git ou ZIP
4. **Configurer les variables d'environnement** :
   - `WEBSITE_SITE_NAME` (automatique)
   - `HTTPS_ONLY=1`
   - `PORT` (automatique)

### 3. Configuration Azure App Service
```bash
# Dans Azure CLI ou Portal
az webapp config set --name votre-app --resource-group votre-rg --startup-file "start_azure.py"
```

### 4. Tester la Connexion
```bash
# Tester les WebSockets
python test_azure_websocket.py https://votre-app.azurewebsites.net
```

## Diagnostic des Problèmes

### 1. Vérifier les Logs Azure
```bash
# Dans Azure Portal > App Service > Logs
# Chercher les erreurs WebSocket
```

### 2. Tester les Endpoints
```bash
# Test endpoint timer
curl https://votre-app.azurewebsites.net/timer

# Test endpoint timer/start
curl -X POST https://votre-app.azurewebsites.net/timer/start
```

### 3. Vérifier la Console Navigateur
- Ouvrir F12 > Console
- Chercher les erreurs WebSocket
- Vérifier les tentatives de connexion

## Configuration WebSocket Azure

### Protocoles Supportés
- **HTTPS** → `wss://` (WebSocket Secure)
- **HTTP** → `ws://` (WebSocket standard)

### Fallback Automatique
Le code implémente un fallback automatique :
1. Essaie `wss://` sur HTTPS
2. Si échec, essaie `ws://`
3. Si échec, utilise le mode HTTP polling

## Variables d'Environnement Azure

```bash
# Variables automatiques Azure
WEBSITE_SITE_NAME=votre-app
WEBSITE_RESOURCE_GROUP=votre-rg
HTTPS_ONLY=1
PORT=8000
```

## Monitoring

### Logs à Surveiller
- Connexions WebSocket
- Erreurs de timeout
- Tentatives de reconnexion
- Mode fallback activé

### Métriques Importantes
- Temps de réponse `/timer`
- Connexions WebSocket actives
- Erreurs 500/502/503

## Rollback en Cas de Problème

Si le déploiement pose problème :

1. **Revenir à la version précédente** via Azure Portal
2. **Vérifier les logs** pour identifier le problème
3. **Tester localement** avec `python start_azure.py`
4. **Redéployer** après correction

## Support

En cas de problème persistant :
1. Vérifier les logs Azure App Service
2. Tester avec `test_azure_websocket.py`
3. Vérifier la configuration CORS
4. Contacter le support Azure si nécessaire
