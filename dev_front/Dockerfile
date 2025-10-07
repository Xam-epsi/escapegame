# Dockerfile pour frontend Next.js (build + run dans le même container)
FROM node:20
WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer toutes les dépendances
RUN npm install

# Copier tout le code source
COPY . .

# Construire l'application Next.js
RUN npm run build

# Exposer le port
EXPOSE 3000

# Lancer le serveur Next.js
CMD ["npm", "run", "start"]


