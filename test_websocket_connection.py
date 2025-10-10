#!/usr/bin/env python3
"""
Script de test pour diagnostiquer les problèmes de connexion WebSocket
"""
import asyncio
import websockets
import json
import time
import sys
import requests
from urllib.parse import urlparse

async def test_websocket_connection(url):
    """Teste la connexion WebSocket avec logs détaillés"""
    print(f"🔌 Test de connexion WebSocket: {url}")
    
    try:
        async with websockets.connect(url, timeout=10) as websocket:
            print("✅ Connexion WebSocket établie")
            
            # Attendre un message du serveur
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Message reçu: {message}")
                
                # Parser le message JSON
                try:
                    data = json.loads(message)
                    print(f"📊 Données parsées: {data}")
                    
                    if data.get("type") == "timer_update":
                        print("✅ Message de timer reçu correctement")
                        return True
                    else:
                        print(f"⚠️  Type de message inattendu: {data.get('type')}")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Erreur parsing JSON: {e}")
                    return False
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout - aucun message reçu du serveur")
                return False
                
    except websockets.exceptions.InvalidURI as e:
        print(f"❌ URI WebSocket invalide: {e}")
        return False
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connexion WebSocket fermée: {e}")
        return False
    except websockets.exceptions.InvalidHandshake as e:
        print(f"❌ Poignée de main WebSocket invalide: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur WebSocket: {e}")
        print(f"   Type d'erreur: {type(e).__name__}")
        return False

def test_timer_endpoints(base_url):
    """Teste les endpoints HTTP du timer"""
    print(f"🔍 Test des endpoints HTTP: {base_url}")
    
    endpoints = [
        ("/timer", "GET"),
        ("/timer/start", "POST"),
        ("/timer/sync", "POST"),
        ("/debug/state", "GET")
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
                print(f"   Réponse: {data}")
                results.append(True)
            else:
                print(f"❌ {method} {endpoint}: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Erreur: {error_data}")
                except:
                    print(f"   Réponse: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {method} {endpoint}: Exception - {e}")
            results.append(False)
    
    return results

async def test_websocket_protocols(base_url):
    """Teste les protocoles WebSocket (ws:// et wss://)"""
    parsed_url = urlparse(base_url)
    
    protocols = []
    if parsed_url.scheme == "https":
        protocols.append(f"wss://{parsed_url.netloc}/timer/ws")
        protocols.append(f"ws://{parsed_url.netloc}/timer/ws")
    else:
        protocols.append(f"ws://{parsed_url.netloc}/timer/ws")
    
    results = []
    
    for protocol_url in protocols:
        print(f"\n🔌 Test du protocole: {protocol_url}")
        result = await test_websocket_connection(protocol_url)
        results.append((protocol_url, result))
    
    return results

async def main():
    """Fonction principale de test"""
    if len(sys.argv) < 2:
        print("Usage: python test_websocket_connection.py <base_url>")
        print("Exemple: python test_websocket_connection.py http://localhost:8000")
        print("Exemple: python test_websocket_connection.py https://votre-app.azurewebsites.net")
        sys.exit(1)
    
    base_url = sys.argv[1]
    parsed_url = urlparse(base_url)
    
    print("🧪 Diagnostic des connexions WebSocket")
    print(f"   URL de base: {base_url}")
    print(f"   Protocole: {parsed_url.scheme}")
    print(f"   Host: {parsed_url.netloc}")
    print()
    
    # Test 1: Endpoints HTTP
    print("📋 Test 1: Endpoints HTTP")
    http_results = test_timer_endpoints(base_url)
    print()
    
    # Test 2: Connexions WebSocket
    print("📋 Test 2: Connexions WebSocket")
    websocket_results = await test_websocket_protocols(base_url)
    print()
    
    # Résumé
    print("📊 Résumé des tests:")
    
    http_passed = sum(http_results)
    http_total = len(http_results)
    print(f"   Endpoints HTTP: {http_passed}/{http_total} réussis")
    
    websocket_passed = sum(1 for _, result in websocket_results if result)
    websocket_total = len(websocket_results)
    print(f"   Connexions WebSocket: {websocket_passed}/{websocket_total} réussies")
    
    for protocol_url, result in websocket_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"     {status} {protocol_url}")
    
    total_passed = http_passed + websocket_passed
    total_tests = http_total + websocket_total
    
    print(f"\n🎯 Résultat global: {total_passed}/{total_tests} tests réussis")
    
    if total_passed == total_tests:
        print("🎉 Tous les tests sont passés ! Les connexions WebSocket fonctionnent.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        
        if http_passed < http_total:
            print("   - Problème avec les endpoints HTTP")
        if websocket_passed < websocket_total:
            print("   - Problème avec les connexions WebSocket")
            print("   - Vérifiez la configuration Azure pour les WebSockets")

if __name__ == "__main__":
    asyncio.run(main())
