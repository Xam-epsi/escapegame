# Guide de Normalisation des Codes

## Problème Identifié

**Symptôme** : Le bon code `ru-0001` + `5309` donne une défaite au lieu d'une victoire

**Cause** : Sensibilité à la casse et aux espaces dans la comparaison des codes

## Analyse du Problème

### 1. **Fichier de Mapping**
```csv
site_code;shutdown_code
RU-0001;5309
```

### 2. **Code Utilisé**
```
Pipeline: ru-0001  (minuscules)
Code: 5309
```

### 3. **Problème de Comparaison**
- **Mapping** : `RU-0001` (majuscules)
- **Utilisé** : `ru-0001` (minuscules)
- **Résultat** : Pas de correspondance → Défaite

## Solution Implémentée

### ✅ **Normalisation des Site Codes**
```python
# Avant
expected = globals.CURRENT_SECRETS.get(site) or globals.MAPPING.get(site)

# Maintenant
site_normalized = site.upper().strip()
for key, value in globals.CURRENT_SECRETS.items():
    if key.upper().strip() == site_normalized:
        expected = value
        break
```

### ✅ **Normalisation des Codes**
```python
# Avant
if payload.code_a == expected:

# Maintenant
code_normalized = str(code_a).strip()
expected_normalized = str(expected).strip()
if code_normalized == expected_normalized:
```

## Formats Supportés

### Site Codes
- ✅ `ru-0001` (minuscules)
- ✅ `RU-0001` (majuscules)
- ✅ `ru-0001 ` (avec espace)
- ✅ ` RU-0001` (espace au début)
- ✅ `Ru-0001` (mélange)

### Codes Secrets
- ✅ `5309` (normal)
- ✅ ` 5309` (avec espace au début)
- ✅ `5309 ` (avec espace à la fin)
- ✅ ` 5309 ` (espaces des deux côtés)

## Tests de Validation

### Test Automatique
```bash
python test_code_normalization.py https://votre-app.azurewebsites.net
```

### Tests Inclus
1. **Codes valides** avec différents formats
2. **Codes invalides** (doivent être rejetés)
3. **Espaces** dans les codes
4. **Casse** différente

## Logs de Debug

### Logs Ajoutés
```
🔍 Site normalisé: 'ru-0001' → 'RU-0001'
🔍 Trouvé dans MAPPING: RU-0001 → 5309
🔍 Comparaison normalisée:
   Code fourni: '5309' → '5309'
   Code attendu: '5309' → '5309'
✅ Code correct - victoire !
```

### Vérification
Chercher dans les logs :
- `🔍 Site normalisé` - Normalisation du site
- `🔍 Trouvé dans` - Recherche du code
- `🔍 Comparaison normalisée` - Comparaison des codes
- `✅ Code correct` - Succès

## Cas d'Usage

### 1. **Code Correct avec Normalisation**
```
Pipeline: ru-0001
Code: 5309
→ ✅ Popup de victoire
```

### 2. **Code Incorrect**
```
Pipeline: ru-0001
Code: 1234
→ ❌ Popup de défaite
```

### 3. **Site Invalide**
```
Pipeline: invalid-site
Code: 5309
→ ❌ Popup de défaite
```

## Prévention

### 1. **Validation Côté Client**
- Normaliser les entrées avant l'envoi
- Afficher les formats acceptés

### 2. **Messages d'Aide**
- Indiquer les formats supportés
- Guider l'utilisateur

### 3. **Tests Réguliers**
- Vérifier la normalisation
- Tester différents formats

## Monitoring

### Logs à Surveiller
- `🔍 Site normalisé` - Problèmes de normalisation
- `❌ Site non trouvé` - Sites invalides
- `✅ Code correct` - Succès
- `❌ Code incorrect` - Échecs

### Métriques
- Taux de succès des normalisations
- Types d'erreurs de format
- Temps de traitement des codes

## Dépannage

### Problème : Code rejeté malgré normalisation
1. Vérifier les logs de normalisation
2. Comparer les formats dans les logs
3. Tester avec le script de test

### Problème : Code accepté alors qu'il est invalide
1. Vérifier la logique de normalisation
2. Tester avec des codes invalides
3. Vérifier les espaces et caractères spéciaux

### Problème : Site non trouvé
1. Vérifier le fichier mapping_codes.csv
2. Vérifier la normalisation des clés
3. Tester avec différents formats de site
