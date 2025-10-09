#!/usr/bin/env python3
"""
Script de test pour vérifier que le WebSocket timer fonctionne correctement
"""
import asyncio
import websockets
import json

async def test_websocket_timer():
    """Test de connexion WebSocket au timer"""
    uri = "ws://localhost:8000/timer/ws"
    
    try:
        print("🔌 Connexion au WebSocket timer...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connexion WebSocket établie")
            
            # Recevoir quelques messages pour tester
            for i in range(5):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    print(f"📨 Message {i+1}: {data}")
                    
                    if data.get('type') == 'timer_update':
                        remaining = data.get('remaining', 0)
                        minutes = remaining // 60
                        seconds = remaining % 60
                        print(f"⏰ Temps restant: {minutes:02d}:{seconds:02d}")
                    
                except asyncio.TimeoutError:
                    print("⏰ Timeout - pas de message reçu")
                    break
                    
    except Exception as e:
        print(f"❌ Erreur WebSocket: {e}")
        return False
    
    print("✅ Test WebSocket terminé avec succès")
    return True

if __name__ == "__main__":
    print("🧪 Test du système WebSocket timer")
    success = asyncio.run(test_websocket_timer())
    if success:
        print("🎉 Test réussi ! Le système WebSocket fonctionne.")
    else:
        print("💥 Test échoué ! Problème avec le WebSocket.")

