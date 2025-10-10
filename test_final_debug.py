#!/usr/bin/env python3
"""
Script de debug pour l'endpoint /final
"""
import requests
import json
import sys

def test_debug_state(base_url):
    """Teste l'endpoint de debug pour voir l'état du jeu"""
    print("🔍 Test de l'état du jeu")
    
    try:
        response = requests.get(f"{base_url}/debug/state", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ État du jeu:")
            print(f"   CURRENT_SECRETS: {data.get('CURRENT_SECRETS', {})}")
            print(f"   MAPPING: {data.get('MAPPING', {})}")
            print(f"   GAME_COMPLETED: {data.get('GAME_COMPLETED', False)}")
            return data
        else:
            print(f"❌ Erreur debug state: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception debug state: {e}")
        return None

def test_validate_endpoint(base_url):
    """Teste l'endpoint /validate pour créer des secrets"""
    print("🔍 Test de l'endpoint /validate")
    
    # Données de test pour la validation
    test_scores = [
        {"site_code": "RU001", "score": 85.5},
        {"site_code": "RU002", "score": 92.3}
    ]
    
    try:
        response = requests.post(
            f"{base_url}/validate",
            json={"scores": test_scores},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Validation réussie: {data}")
            return data
        else:
            print(f"❌ Erreur validation: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Détail: {error_data}")
            except:
                print(f"   Réponse: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception validation: {e}")
        return None

def test_final_endpoint(base_url, site_code, code_a):
    """Teste l'endpoint /final avec des paramètres spécifiques"""
    print(f"🔍 Test de l'endpoint /final avec site={site_code}, code={code_a}")
    
    try:
        response = requests.post(
            f"{base_url}/final",
            json={"site_code": site_code, "code_a": code_a},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Final réussie: {data}")
            return data
        else:
            print(f"❌ Erreur final: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Détail: {error_data}")
            except:
                print(f"   Réponse: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception final: {e}")
        return None

def main():
    """Fonction principale de debug"""
    if len(sys.argv) < 2:
        print("Usage: python test_final_debug.py <base_url>")
        print("Exemple: python test_final_debug.py http://localhost:8000")
        print("Exemple: python test_final_debug.py https://votre-app.azurewebsites.net")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    print("🧪 Debug de l'endpoint /final")
    print(f"   URL de base: {base_url}")
    print()
    
    # 1. Vérifier l'état initial
    print("📋 Étape 1: Vérification de l'état initial")
    initial_state = test_debug_state(base_url)
    print()
    
    # 2. Tester la validation pour créer des secrets
    print("📋 Étape 2: Test de validation pour créer des secrets")
    validation_result = test_validate_endpoint(base_url)
    print()
    
    # 3. Vérifier l'état après validation
    print("📋 Étape 3: Vérification de l'état après validation")
    post_validation_state = test_debug_state(base_url)
    print()
    
    # 4. Tester l'endpoint final
    if post_validation_state and post_validation_state.get('CURRENT_SECRETS'):
        secrets = post_validation_state['CURRENT_SECRETS']
        print("📋 Étape 4: Test de l'endpoint /final")
        
        for site_code, secret_code in secrets.items():
            print(f"   Test avec site={site_code}, code={secret_code}")
            final_result = test_final_endpoint(base_url, site_code, secret_code)
            print()
            
            # Test avec un code incorrect
            print(f"   Test avec code incorrect pour site={site_code}")
            final_result_wrong = test_final_endpoint(base_url, site_code, "WRONG_CODE")
            print()
            break  # Tester seulement le premier secret
    else:
        print("❌ Aucun secret disponible pour tester /final")
    
    print("✅ Debug terminé")

if __name__ == "__main__":
    main()
