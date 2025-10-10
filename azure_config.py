# Configuration spéciale pour Azure
import os

# Configuration pour Azure App Service
AZURE_CONFIG = {
    # Configuration WebSocket pour Azure
    "websocket": {
        "enabled": True,
        "timeout": 30,  # Timeout en secondes
        "ping_interval": 20,  # Ping toutes les 20 secondes
        "max_connections": 100
    },
    
    # Configuration CORS pour Azure
    "cors": {
        "allow_origins": ["*"],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"]
    },
    
    # Configuration du timer
    "timer": {
        "duration": 30 * 60,  # 30 minutes
        "sync_interval": 1,  # Synchronisation toutes les secondes
        "fallback_enabled": True
    }
}

# Variables d'environnement Azure
def get_azure_config():
    """Récupère la configuration Azure depuis les variables d'environnement"""
    return {
        "is_azure": os.getenv("WEBSITE_SITE_NAME") is not None,
        "site_name": os.getenv("WEBSITE_SITE_NAME", ""),
        "resource_group": os.getenv("WEBSITE_RESOURCE_GROUP", ""),
        "subscription_id": os.getenv("WEBSITE_OWNER_NAME", ""),
        "https_only": os.getenv("HTTPS_ONLY", "1") == "1"
    }

# Configuration du serveur pour Azure
def get_server_config():
    """Configuration du serveur optimisée pour Azure"""
    azure_info = get_azure_config()
    
    config = {
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", 8000)),
        "workers": 1,  # Azure App Service recommande 1 worker
        "reload": False,  # Désactiver le reload en production
        "log_level": "info"
    }
    
    if azure_info["is_azure"]:
        print("🔵 Configuration Azure détectée")
        print(f"   Site: {azure_info['site_name']}")
        print(f"   HTTPS Only: {azure_info['https_only']}")
        
        # Configuration spéciale pour Azure
        config.update({
            "timeout_keep_alive": 2,
            "timeout_graceful_shutdown": 30,
            "limit_concurrency": 1000,
            "limit_max_requests": 1000
        })
    
    return config
