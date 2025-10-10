# Guide de Diagnostic - Erreur EventSource Timer

## Problème Identifié

**Erreur** : `EventSource timer: Event`
**Cause** : Problème de connexion WebSocket ou de communication avec le serveur

## Causes Possibles

### 1. **Problème de Connexion WebSocket**
- Connexion WebSocket fermée inattendument
- Timeout de connexion
- Problème de protocole (ws:// vs wss://)

### 2. **Problème de Serveur**
- Serveur non accessible
- Endpoint `/timer/ws` non disponible
- Problème de configuration Azure

### 3. **Problème de Réseau**
- Connexion internet instable
- Firewall bloquant les WebSockets
- Problème de proxy

## Solutions Implémentées

### ✅ **Logs de Debug Améliorés**
```javascript
// Détails de l'erreur WebSocket
console.error('❌ Erreur WebSocket timer:', event);
console.error('   Détails de l\'erreur:', {
  type: event.type,
  target: event.target,
  readyState: event.target?.readyState,
  url: event.target?.url
});
```

### ✅ **Gestion d'Erreur HTTP Améliorée**
```javascript
// Logs détaillés pour les erreurs HTTP
if (!res.ok) {
  console.error(`❌ Erreur HTTP timer fallback: ${res.status} ${res.statusText}`);
}
```

### ✅ **Fallback Automatique**
- Tentative de reconnexion WebSocket
- Passage au mode HTTP polling
- Gestion des erreurs de réseau

## Diagnostic

### 1. **Vérifier la Console du Navigateur**
Ouvrir F12 > Console et chercher :
- `❌ Erreur WebSocket timer`
- `❌ Erreur HTTP timer fallback`
- `🔌 Connexion WebSocket timer`
- `🔄 Démarrage du mode fallback HTTP`

### 2. **Utiliser le Script de Test**
```bash
python test_websocket_connection.py https://votre-app.azurewebsites.net
```

### 3. **Vérifier les Endpoints**
```bash
# Test des endpoints
curl https://votre-app.azurewebsites.net/timer
curl -X POST https://votre-app.azurewebsites.net/timer/start
```

## Solutions par Type d'Erreur

### Erreur WebSocket
**Symptôme** : `❌ Erreur WebSocket timer`
**Solutions** :
1. Vérifier la configuration Azure pour les WebSockets
2. Tester avec `ws://` au lieu de `wss://`
3. Vérifier les logs serveur

### Erreur HTTP
**Symptôme** : `❌ Erreur HTTP timer fallback`
**Solutions** :
1. Vérifier que le serveur est accessible
2. Tester les endpoints individuellement
3. Vérifier la configuration CORS

### Timeout de Connexion
**Symptôme** : `⏰ Timeout - aucun message reçu`
**Solutions** :
1. Vérifier la latence réseau
2. Augmenter le timeout
3. Tester avec une connexion plus stable

## Configuration Azure

### 1. **WebSockets sur Azure**
```xml
<!-- Dans web.config -->
<webSocket enabled="true" />
```

### 2. **Variables d'Environnement**
```bash
WEBSITE_SITE_NAME=votre-app
HTTPS_ONLY=1
PORT=8000
```

### 3. **Configuration CORS**
```python
# Dans backend/main.py
cors_origins = [
    "https://*.azurewebsites.net",
    "https://*.azurestaticapps.net"
]
```

## Tests de Validation

### Test Automatique
```bash
# Test complet des connexions
python test_websocket_connection.py https://votre-app.azurewebsites.net
```

### Test Manuel
1. Ouvrir la console du navigateur (F12)
2. Recharger la page
3. Observer les logs de connexion
4. Vérifier les erreurs

## Monitoring

### Logs à Surveiller
- `🔌 Connexion WebSocket timer` - Tentatives de connexion
- `❌ Erreur WebSocket timer` - Erreurs de connexion
- `🔄 Démarrage du mode fallback` - Passage au mode HTTP
- `✅ WebSocket timer connecté` - Connexion réussie

### Métriques Importantes
- Taux de succès des connexions WebSocket
- Nombre de reconnexions
- Temps de réponse des endpoints
- Erreurs de timeout

## Prévention

### 1. **Configuration Robuste**
- Fallback automatique HTTP
- Reconnexion automatique
- Gestion des erreurs de réseau

### 2. **Monitoring Continu**
- Surveillance des logs
- Alertes en cas d'erreur
- Tests de connectivité réguliers

### 3. **Configuration Azure**
- WebSockets activés
- CORS configuré
- Variables d'environnement correctes

## Dépannage

### Problème : WebSocket ne se connecte pas
1. Vérifier la configuration Azure
2. Tester avec `ws://` au lieu de `wss://`
3. Vérifier les logs serveur

### Problème : Mode fallback ne fonctionne pas
1. Vérifier les endpoints HTTP
2. Tester la connectivité réseau
3. Vérifier la configuration CORS

### Problème : Reconnexion échoue
1. Vérifier la stabilité du réseau
2. Augmenter les délais de reconnexion
3. Implémenter un backoff exponentiel
