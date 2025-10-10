#!/usr/bin/env python3
"""
Script de test pour diagnostiquer les problèmes WebSocket sur Azure
"""
import asyncio
import websockets
import json
import time
import sys
from urllib.parse import urlparse

async def test_websocket_connection(url):
    """Teste la connexion WebSocket"""
    print(f"🔌 Test de connexion WebSocket: {url}")
    
    try:
        async with websockets.connect(url) as websocket:
            print("✅ Connexion WebSocket établie")
            
            # Envoyer un message de test
            test_message = {
                "type": "test",
                "message": "Test de connexion",
                "timestamp": time.time()
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Message de test envoyé")
            
            # Attendre une réponse
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Réponse reçue: {response}")
                return True
            except asyncio.TimeoutError:
                print("⏰ Timeout - aucune réponse reçue")
                return False
                
    except websockets.exceptions.InvalidURI:
        print("❌ URI WebSocket invalide")
        return False
    except websockets.exceptions.ConnectionClosed:
        print("❌ Connexion WebSocket fermée")
        return False
    except Exception as e:
        print(f"❌ Erreur WebSocket: {e}")
        return False

async def test_timer_endpoint(base_url):
    """Teste l'endpoint /timer"""
    import aiohttp
    
    print(f"🔌 Test de l'endpoint /timer: {base_url}/timer")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/timer") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Endpoint /timer OK: {data}")
                    return True
                else:
                    print(f"❌ Endpoint /timer erreur: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Erreur endpoint /timer: {e}")
        return False

async def test_timer_start_endpoint(base_url):
    """Teste l'endpoint /timer/start"""
    import aiohttp
    
    print(f"🔌 Test de l'endpoint /timer/start: {base_url}/timer/start")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/timer/start") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Endpoint /timer/start OK: {data}")
                    return True
                else:
                    print(f"❌ Endpoint /timer/start erreur: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Erreur endpoint /timer/start: {e}")
        return False

async def main():
    """Fonction principale de test"""
    if len(sys.argv) < 2:
        print("Usage: python test_azure_websocket.py <base_url>")
        print("Exemple: python test_azure_websocket.py https://votre-app.azurewebsites.net")
        sys.exit(1)
    
    base_url = sys.argv[1]
    parsed_url = urlparse(base_url)
    
    print("🧪 Test de diagnostic Azure WebSocket")
    print(f"   URL de base: {base_url}")
    print(f"   Protocole: {parsed_url.scheme}")
    print(f"   Host: {parsed_url.netloc}")
    
    # Test des endpoints HTTP
    print("\n📡 Test des endpoints HTTP...")
    await test_timer_endpoint(base_url)
    await test_timer_start_endpoint(base_url)
    
    # Test WebSocket
    print("\n🔌 Test des connexions WebSocket...")
    
    # Test wss:// (pour HTTPS)
    if parsed_url.scheme == "https":
        ws_url = f"wss://{parsed_url.netloc}/timer/ws"
        await test_websocket_connection(ws_url)
    
    # Test ws:// (fallback)
    ws_url = f"ws://{parsed_url.netloc}/timer/ws"
    await test_websocket_connection(ws_url)
    
    print("\n✅ Tests terminés")

if __name__ == "__main__":
    asyncio.run(main())
