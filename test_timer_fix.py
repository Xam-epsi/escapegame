#!/usr/bin/env python3
"""
Script de test pour vérifier que les corrections du timer fonctionnent
"""
import requests
import json
import time
import sys

def test_timer_endpoints(base_url):
    """Teste les endpoints du timer"""
    print("🧪 Test des endpoints du timer")
    
    # Test GET /timer
    try:
        response = requests.get(f"{base_url}/timer", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /timer OK: {data}")
        else:
            print(f"❌ GET /timer erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GET /timer exception: {e}")
        return False
    
    # Test POST /timer/start
    try:
        response = requests.post(f"{base_url}/timer/start", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ POST /timer/start OK: {data}")
        else:
            print(f"❌ POST /timer/start erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ POST /timer/start exception: {e}")
        return False
    
    # Test POST /timer/sync
    try:
        response = requests.post(f"{base_url}/timer/sync", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ POST /timer/sync OK: {data}")
        else:
            print(f"❌ POST /timer/sync erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ POST /timer/sync exception: {e}")
        return False
    
    return True

def test_websocket_simulation(base_url):
    """Simule le comportement WebSocket avec des requêtes HTTP"""
    print("🔌 Simulation du comportement WebSocket")
    
    # Démarrer le timer
    try:
        response = requests.post(f"{base_url}/timer/start", timeout=10)
        if response.status_code != 200:
            print(f"❌ Impossible de démarrer le timer: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur démarrage timer: {e}")
        return False
    
    # Tester plusieurs requêtes pour simuler les mises à jour
    for i in range(3):
        try:
            response = requests.get(f"{base_url}/timer", timeout=10)
            if response.status_code == 200:
                data = response.json()
                remaining = data.get('remaining', 0)
                print(f"   Mise à jour {i+1}: {remaining}s restantes")
            else:
                print(f"❌ Erreur mise à jour {i+1}: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Exception mise à jour {i+1}: {e}")
            return False
        
        time.sleep(1)
    
    return True

def test_game_reset(base_url):
    """Teste la réinitialisation du jeu"""
    print("🔄 Test de réinitialisation du jeu")
    
    try:
        response = requests.post(f"{base_url}/game/reset", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Game reset OK: {data}")
            return True
        else:
            print(f"❌ Game reset erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Game reset exception: {e}")
        return False

def main():
    """Fonction principale de test"""
    if len(sys.argv) < 2:
        print("Usage: python test_timer_fix.py <base_url>")
        print("Exemple: python test_timer_fix.py http://localhost:8000")
        print("Exemple: python test_timer_fix.py https://votre-app.azurewebsites.net")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    print("🧪 Test des corrections du timer")
    print(f"   URL de base: {base_url}")
    print()
    
    # Tests
    tests = [
        ("Endpoints Timer", lambda: test_timer_endpoints(base_url)),
        ("Simulation WebSocket", lambda: test_websocket_simulation(base_url)),
        ("Réinitialisation Jeu", lambda: test_game_reset(base_url))
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"📋 {test_name}...")
        try:
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
        print("🎉 Tous les tests sont passés ! Le timer devrait fonctionner sur Azure.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main()
