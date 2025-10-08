#!/bin/bash

# -------------------------------
# Script d'installation et lancement avec barre de progression
# -------------------------------

# Couleurs
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # Reset

echo -e "${BLUE}🚀 Démarrage du setup pour le projet Pipeline Rescue${NC}"

VENV_DIR="venv"

# Création du venv
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}🛠️  Création de l'environnement virtuel...${NC}"
    python -m venv $VENV_DIR
else
    echo -e "${GREEN}✅ Environnement virtuel déjà existant${NC}"
fi

# Activation du venv
echo -e "${BLUE}⚡ Activation de l'environnement virtuel${NC}"
source $VENV_DIR/bin/activate || source $VENV_DIR/Scripts/activate

# Mise à jour de pip
echo -e "${YELLOW}⬆️  Mise à jour de pip...${NC}"
pip install --upgrade pip

# Désinstallation des versions conflictuelles
echo -e "${YELLOW}🧹 Nettoyage des packages OpenCV et numpy...${NC}"
pip uninstall -y opencv-contrib-python opencv-python numpy

# Installation des packages
echo -e "${BLUE}📦 Installation des dépendances...${NC}"
PACKAGES=(
    "numpy<2.0"
    "opencv-contrib-python==4.7.0.72"
    "fastapi==0.95.2"
    "uvicorn[standard]==0.22.0"
    "pandas==2.2.3"
    "scikit-learn==1.3.2"
    "joblib==1.3.2"
    "python-multipart==0.0.6"
    "python-dotenv==1.0.0"
    "pytest==7.4.2"
    "pytest-asyncio==0.21.0"
    "httpx==0.24.1"
    "jinja2==3.1.6"
    "pydantic==2.10.7"
)

COUNT=${#PACKAGES[@]}
for i in "${!PACKAGES[@]}"; do
    pkg=${PACKAGES[$i]}
    echo -e "${YELLOW}[$((i+1))/$COUNT] Installation de $pkg...${NC}"
    pip install $pkg | while read line; do
        echo -ne "\r$line"
    done
    echo -e "${GREEN}✔ $pkg installé${NC}"
done

# Barre de progression finale
echo -e -n "${BLUE}🔧 Finalisation : ${NC}"
for i in {1..20}; do
    echo -ne "▇"
    sleep 0.05
done
echo -e " ${GREEN}Done!${NC}"

# Lancer le serveur
echo -e "${BLUE}🌐 Lancement du serveur FastAPI...${NC}"
uvicorn backend.main:app --reload
