#!/usr/bin/env python3
"""
Script de test pour vérifier les popups de victoire et défaite
"""
import requests
import json
import sys

def test_final_with_invalid_site(base_url):
    """Teste /final avec un site_code invalide (doit afficher popup défaite)"""
    print("🧪 Test avec site_code invalide (doit afficher popup défaite)")
    
    try:
        response = requests.post(
            f"{base_url}/final",
            json={"site_code": "INVALID_SITE", "code_a": "1234"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue: {data}")
            if data.get("result") == "defeat":
                print("✅ Popup de défaite correctement déclenchée")
                return True
            else:
                print(f"❌ Résultat inattendu: {data.get('result')}")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Détail: {error_data}")
            except:
                print(f"   Réponse: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_final_with_invalid_code(base_url, valid_site, valid_code):
    """Teste /final avec un code incorrect (doit afficher popup défaite)"""
    print(f"🧪 Test avec code incorrect pour site {valid_site}")
    
    try:
        response = requests.post(
            f"{base_url}/final",
            json={"site_code": valid_site, "code_a": "WRONG_CODE"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue: {data}")
            if data.get("result") == "defeat":
                print("✅ Popup de défaite correctement déclenchée")
                return True
            else:
                print(f"❌ Résultat inattendu: {data.get('result')}")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_final_with_correct_code(base_url, valid_site, valid_code):
    """Teste /final avec le bon code (doit afficher popup victoire)"""
    print(f"🧪 Test avec code correct pour site {valid_site}")
    
    try:
        response = requests.post(
            f"{base_url}/final",
            json={"site_code": valid_site, "code_a": valid_code},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue: {data}")
            if data.get("result") == "success":
                print("✅ Popup de victoire correctement déclenchée")
                return True
            else:
                print(f"❌ Résultat inattendu: {data.get('result')}")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def setup_test_data(base_url):
    """Configure des données de test en validant des scores"""
    print("🔧 Configuration des données de test...")
    
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
            print(f"✅ Données de test configurées: {data}")
            return data.get("detected_site"), data.get("code_secret")
        else:
            print(f"❌ Erreur configuration: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Exception configuration: {e}")
        return None, None

def main():
    """Fonction principale de test"""
    if len(sys.argv) < 2:
        print("Usage: python test_final_popups.py <base_url>")
        print("Exemple: python test_final_popups.py http://localhost:8000")
        print("Exemple: python test_final_popups.py https://votre-app.azurewebsites.net")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    print("🧪 Test des popups de victoire et défaite")
    print(f"   URL de base: {base_url}")
    print()
    
    # 1. Test avec site_code invalide
    print("📋 Test 1: Site code invalide")
    test1_result = test_final_with_invalid_site(base_url)
    print()
    
    # 2. Configuration des données de test
    print("📋 Test 2: Configuration des données de test")
    valid_site, valid_code = setup_test_data(base_url)
    print()
    
    if valid_site and valid_code:
        # 3. Test avec code incorrect
        print("📋 Test 3: Code incorrect")
        test3_result = test_final_with_invalid_code(base_url, valid_site, valid_code)
        print()
        
        # 4. Test avec code correct
        print("📋 Test 4: Code correct")
        test4_result = test_final_with_correct_code(base_url, valid_site, valid_code)
        print()
    else:
        print("❌ Impossible de configurer les données de test")
        test3_result = False
        test4_result = False
    
    # Résumé
    print("📊 Résumé des tests:")
    tests = [
        ("Site invalide → Popup défaite", test1_result),
        ("Code incorrect → Popup défaite", test3_result),
        ("Code correct → Popup victoire", test4_result)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Résultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! Les popups fonctionnent correctement.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main()
