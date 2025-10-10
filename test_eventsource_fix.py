#!/usr/bin/env python3
"""
Script de test pour vérifier la correction EventSource
"""
import requests
import json
import sys
import time

def test_eventsource_endpoint(base_url):
    """Teste l'endpoint EventSource /timer/stream"""
    print("🧪 Test de l'endpoint EventSource /timer/stream")
    
    try:
        response = requests.get(
            f"{base_url}/timer/stream",
            headers={"Accept": "text/event-stream"},
            timeout=10,
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ Endpoint EventSource accessible")
            
            # Lire quelques lignes du stream
            lines_read = 0
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    print(f"   Ligne reçue: {line}")
                    lines_read += 1
                    if lines_read >= 3:  # Lire seulement les 3 premières lignes
                        break
            
            if lines_read > 0:
                print("✅ Données EventSource reçues correctement")
                return True
            else:
                print("❌ Aucune donnée EventSource reçue")
                return False
        else:
            print(f"❌ Erreur EventSource: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception EventSource: {e}")
        return False

def test_timer_endpoints(base_url):
    """Teste les endpoints du timer"""
    print("🧪 Test des endpoints du timer")
    
    endpoints = [
        ("/timer", "GET"),
        ("/timer/start", "POST"),
        ("/timer/sync", "POST")
    ]
    
    results = []
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {method} {endpoint}: OK")
                results.append(True)
            else:
                print(f"❌ {method} {endpoint}: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {method} {endpoint}: Exception - {e}")
            results.append(False)
    
    return results

def test_websocket_fallback(base_url):
    """Teste le fallback WebSocket vers EventSource"""
    print("🧪 Test du fallback WebSocket vers EventSource")
    
    # Simuler une erreur WebSocket en testant l'endpoint EventSource
    try:
        response = requests.get(f"{base_url}/timer/stream", timeout=5)
        if response.status_code == 200:
            print("✅ Fallback EventSource disponible")
            return True
        else:
            print(f"❌ Fallback EventSource non disponible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur fallback EventSource: {e}")
        return False

def main():
    """Fonction principale de test"""
    if len(sys.argv) < 2:
        print("Usage: python test_eventsource_fix.py <base_url>")
        print("Exemple: python test_eventsource_fix.py http://localhost:8000")
        print("Exemple: python test_eventsource_fix.py https://votre-app.azurewebsites.net")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    print("🧪 Test de la correction EventSource")
    print(f"   URL de base: {base_url}")
    print()
    
    # Tests
    tests = [
        ("Endpoints Timer", lambda: test_timer_endpoints(base_url)),
        ("Endpoint EventSource", lambda: test_eventsource_endpoint(base_url)),
        ("Fallback EventSource", lambda: test_websocket_fallback(base_url))
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"📋 {test_name}...")
        try:
            if test_name == "Endpoints Timer":
                result = all(test_func())
            else:
                result = test_func()
            results.append((test_name, result))
            print(f"   {'✅' if result else '❌'} {test_name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"   ❌ {test_name}: EXCEPTION - {e}")
            results.append((test_name, False))
        print()
    
    # Résumé
    print("📊 Résumé des tests:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Résultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! EventSource fonctionne correctement.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        
        if not results[1][1]:  # EventSource endpoint
            print("   - Problème avec l'endpoint EventSource /timer/stream")
        if not results[2][1]:  # Fallback
            print("   - Problème avec le fallback EventSource")

if __name__ == "__main__":
    main()
