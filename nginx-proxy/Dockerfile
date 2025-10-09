FROM nginx:alpine

# Installer OpenSSL
RUN apk add --no-cache openssl bash

# Créer le dossier pour les certificats
RUN mkdir -p /etc/nginx/certs

# Copier la configuration Nginx
COPY default.conf /etc/nginx/conf.d/default.conf

# Script d'entrée pour générer le certificat au démarrage
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
