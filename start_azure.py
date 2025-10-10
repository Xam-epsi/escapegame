#!/usr/bin/env python3
"""
Script de démarrage optimisé pour Azure App Service
"""
import os
import sys
import uvicorn
from azure_config import get_server_config, get_azure_config

def main():
    """Démarre l'application avec la configuration Azure"""
    azure_info = get_azure_config()
    config = get_server_config()
    
    print("🚀 Démarrage de l'application...")
    print(f"   Configuration: {config}")
    print(f"   Azure: {azure_info}")
    
    # Configuration uvicorn pour Azure
    uvicorn.run(
        "backend.main:app",
        host=config["host"],
        port=config["port"],
        workers=config["workers"],
        reload=config["reload"],
        log_level=config["log_level"],
        timeout_keep_alive=config.get("timeout_keep_alive", 2),
        timeout_graceful_shutdown=config.get("timeout_graceful_shutdown", 30),
        limit_concurrency=config.get("limit_concurrency", 1000),
        limit_max_requests=config.get("limit_max_requests", 1000),
        access_log=True
    )

if __name__ == "__main__":
    main()
