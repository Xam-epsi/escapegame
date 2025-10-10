# Correction de l'Erreur EventSource 320

## Problème Identifié

**Erreur** : `EventSource timer: Event {isTrusted: true, type: 'error', target: EventSource, currentTarget: EventSource, eventPhase: 2, …}`
**Code d'erreur** : 320
**Cause** : Problème de connexion EventSource ou WebSocket

## Solutions Implémentées

### ✅ **Fallback EventSource**
- ✅ Ajout d'un endpoint EventSource `/timer/stream`
- ✅ Fallback automatique WebSocket → EventSource → HTTP polling
- ✅ Gestion d'erreur améliorée pour EventSource

### ✅ **Endpoint EventSource Côté Serveur**
```python
@router.get("/timer/stream")
async def timer_stream():
    """Endpoint EventSource pour le timer (fallback)"""
    # Stream en temps réel des données du timer
```

### ✅ **Gestion d'Erreur Améliorée**
```javascript
eventsource.onerror = function(event) {
  console.error('❌ Erreur EventSource timer:', event);
  // Détails complets de l'erreur
  // Fallback vers HTTP polling
};
```

## Architecture de Fallback

### 1. **WebSocket (Priorité 1)**
```
WebSocket → wss://host/timer/ws
↓ (si échec)
EventSource
```

### 2. **EventSource (Priorité 2)**
```
EventSource → https://host/timer/stream
↓ (si échec)
HTTP Polling
```

### 3. **HTTP Polling (Priorité 3)**
```
HTTP → GET /timer (toutes les secondes)
```

## Fonctionnalités EventSource

### ✅ **Stream en Temps Réel**
- Mise à jour automatique du timer
- Synchronisation entre les clients
- Gestion des événements de jeu

### ✅ **Gestion d'Erreur**
- Reconnexion automatique
- Fallback vers HTTP polling
- Logs détaillés pour le debug

### ✅ **Compatibilité**
- Support des navigateurs modernes
- Fallback pour les anciens navigateurs
- Configuration Azure optimisée

## Tests de Validation

### Test Automatique
```bash
python test_eventsource_fix.py https://votre-app.azurewebsites.net
```

### Tests Inclus
1. **Endpoint EventSource** - Vérification de `/timer/stream`
2. **Endpoints Timer** - Vérification des endpoints HTTP
3. **Fallback EventSource** - Test du fallback

## Configuration Azure

### 1. **Headers EventSource**
```python
headers={
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Cache-Control"
}
```

### 2. **Media Type**
```python
media_type="text/event-stream"
```

### 3. **Streaming Response**
```python
return StreamingResponse(
    generate_timer_events(),
    media_type="text/event-stream",
    headers=headers
)
```

## Logs de Debug

### Logs EventSource
- `🔄 Démarrage EventSource timer (fallback)`
- `✅ EventSource timer connecté`
- `📥 Message EventSource reçu`
- `❌ Erreur EventSource timer`

### Logs de Fallback
- `❌ Échec de reconnexion WebSocket, passage au mode EventSource`
- `❌ Échec de reconnexion EventSource, passage au mode HTTP polling`

## Diagnostic

### 1. **Vérifier la Console**
Ouvrir F12 > Console et chercher :
- `❌ Erreur EventSource timer`
- `🔄 Démarrage EventSource timer`
- `✅ EventSource timer connecté`

### 2. **Tester l'Endpoint**
```bash
curl -H "Accept: text/event-stream" https://votre-app.azurewebsites.net/timer/stream
```

### 3. **Vérifier les Headers**
```bash
curl -I https://votre-app.azurewebsites.net/timer/stream
```

## Avantages EventSource

### ✅ **Meilleure Compatibilité**
- Support natif des navigateurs
- Reconnexion automatique
- Gestion d'erreur intégrée

### ✅ **Performance**
- Moins de requêtes HTTP
- Stream en temps réel
- Réduction de la latence

### ✅ **Robustesse**
- Fallback automatique
- Gestion des déconnexions
- Retry automatique

## Prévention des Erreurs

### 1. **Configuration Robuste**
- Fallback en cascade
- Gestion d'erreur complète
- Logs détaillés

### 2. **Tests Réguliers**
- Vérification des endpoints
- Test de connectivité
- Monitoring des erreurs

### 3. **Configuration Azure**
- Headers CORS corrects
- Streaming activé
- Timeout configuré

## Monitoring

### Métriques à Surveiller
- Taux de succès EventSource
- Nombre de reconnexions
- Erreurs de stream
- Latence des mises à jour

### Logs Importants
- `✅ EventSource timer connecté`
- `❌ Erreur EventSource timer`
- `🔄 Tentative de reconnexion EventSource`
- `📥 Message EventSource reçu`

## Dépannage

### Problème : EventSource ne se connecte pas
1. Vérifier l'endpoint `/timer/stream`
2. Tester les headers CORS
3. Vérifier la configuration Azure

### Problème : Stream interrompu
1. Vérifier la stabilité du réseau
2. Tester la reconnexion automatique
3. Vérifier les logs serveur

### Problème : Données corrompues
1. Vérifier le format JSON
2. Tester le parsing des données
3. Vérifier la synchronisation
