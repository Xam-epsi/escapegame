FROM python:3.12-slim

# Définir le dossier de travail
WORKDIR /app

ENV PYTHONPATH=/app

# Copier uniquement le fichier requirements pour installer les dépendances
COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le dossier parent (backend et autres modules)
COPY backend/ ./backend
COPY frontend ./frontend
COPY . .

# Définir le dossier de travail final
WORKDIR /app/backend

EXPOSE 5000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]