#!/bin/sh

# Vérifie si les certificats existent déjà
if [ ! -f /etc/nginx/certs/fullchain.pem ] || [ ! -f /etc/nginx/certs/privkey.pem ]; then
    echo "Génération des certificats auto-signés..."
    openssl req -x509 -nodes -days 365 \
        -newkey rsa:2048 \
        -keyout /etc/nginx/certs/privkey.pem \
        -out /etc/nginx/certs/fullchain.pem \
        -subj "/C=./ST=./L=./O=./CN=."
fi

# Lancer Nginx
exec "$@"
