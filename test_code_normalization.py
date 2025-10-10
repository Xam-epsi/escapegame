#!/usr/bin/env python3
"""
Script de test pour vérifier la normalisation des codes
"""
import requests
import json
import sys

def test_code_normalization(base_url):
    """Teste la normalisation des codes avec différents formats"""
    print("🧪 Test de normalisation des codes")
    
    # Formats de test pour RU-0001
    test_cases = [
        ("ru-0001", "5309"),      # minuscules
        ("RU-0001", "5309"),      # majuscules
        ("ru-0001 ", "5309"),     # avec espace
        (" RU-0001", "5309"),     # espace au début
        ("ru-0001", " 5309"),     # espace dans le code
        ("RU-0001", "5309 "),     # espace à la fin du code
    ]
    
    results = []
    
    for site_code, code in test_cases:
        print(f"\n📋 Test: site='{site_code}', code='{code}'")
        
        try:
            response = requests.post(
                f"{base_url}/final",
                json={"site_code": site_code, "code_a": code},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result")
                message = data.get("message", "")
                
                print(f"   Statut: {response.status_code}")
                print(f"   Résultat: {result}")
                print(f"   Message: {message}")
                
                if result == "success":
                    print("   ✅ SUCCÈS - Code accepté !")
                    results.append(True)
                elif result == "defeat":
                    print("   ❌ DÉFAITE - Code rejeté")
                    results.append(False)
                else:
                    print(f"   ⚠️  RÉSULTAT INATTENDU: {result}")
                    results.append(False)
            else:
                print(f"   ❌ Erreur HTTP: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Détail: {error_data}")
                except:
                    print(f"   Réponse: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append(False)
    
    return results

def test_invalid_codes(base_url):
    """Teste avec des codes invalides pour vérifier qu'ils sont rejetés"""
    print("\n🧪 Test avec codes invalides (doivent être rejetés)")
    
    invalid_cases = [
        ("ru-0001", "1234"),      # mauvais code
        ("ru-0001", "WRONG"),     # code textuel
        ("invalid-site", "5309"), # mauvais site
    ]
    
    results = []
    
    for site_code, code in invalid_cases:
        print(f"\n📋 Test invalide: site='{site_code}', code='{code}'")
        
        try:
            response = requests.post(
                f"{base_url}/final",
                json={"site_code": site_code, "code_a": code},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result")
                message = data.get("message", "")
                
                print(f"   Statut: {response.status_code}")
                print(f"   Résultat: {result}")
                print(f"   Message: {message}")
                
                if result == "defeat":
                    print("   ✅ CORRECT - Code invalide rejeté")
                    results.append(True)
                else:
                    print(f"   ❌ PROBLÈME - Code invalide accepté: {result}")
                    results.append(False)
            else:
                print(f"   ❌ Erreur HTTP: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append(False)
    
    return results

def main():
    """Fonction principale de test"""
    if len(sys.argv) < 2:
        print("Usage: python test_code_normalization.py <base_url>")
        print("Exemple: python test_code_normalization.py http://localhost:8000")
        print("Exemple: python test_code_normalization.py https://votre-app.azurewebsites.net")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    print("🧪 Test de normalisation des codes")
    print(f"   URL de base: {base_url}")
    print()
    
    # Test 1: Codes valides avec différents formats
    print("📋 Test 1: Codes valides avec normalisation")
    valid_results = test_code_normalization(base_url)
    
    # Test 2: Codes invalides
    print("\n📋 Test 2: Codes invalides")
    invalid_results = test_invalid_codes(base_url)
    
    # Résumé
    print("\n📊 Résumé des tests:")
    
    valid_passed = sum(valid_results)
    valid_total = len(valid_results)
    print(f"   Codes valides: {valid_passed}/{valid_total} réussis")
    
    invalid_passed = sum(invalid_results)
    invalid_total = len(invalid_results)
    print(f"   Codes invalides: {invalid_passed}/{invalid_total} correctement rejetés")
    
    total_passed = valid_passed + invalid_passed
    total_tests = valid_total + invalid_total
    
    print(f"\n🎯 Résultat global: {total_passed}/{total_tests} tests réussis")
    
    if total_passed == total_tests:
        print("🎉 Tous les tests sont passés ! La normalisation fonctionne correctement.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        
        if valid_passed < valid_total:
            print("   - Problème avec la normalisation des codes valides")
        if invalid_passed < invalid_total:
            print("   - Problème avec le rejet des codes invalides")

if __name__ == "__main__":
    main()
