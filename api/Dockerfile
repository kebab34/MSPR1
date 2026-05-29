# Image de base : Python 3.11 en version "slim" (allégée, sans outils inutiles)
FROM python:3.11-slim

# Définit /app comme répertoire de travail dans le conteneur (tous les COPY/RUN se font depuis ici)
WORKDIR /app

# Installe les dépendances système nécessaires :
# - gcc : compilateur C requis par certaines librairies Python (ex: psycopg2)
# - postgresql-client : outils PostgreSQL en ligne de commande (utile pour déboguer)
# rm -rf /var/lib/apt/lists/* : supprime le cache apt pour réduire la taille de l'image
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copie uniquement requirements.txt en premier (optimisation du cache Docker)
# Si requirements.txt ne change pas, Docker réutilise le cache et ne réinstalle pas tout
COPY requirements.txt .

# Installe toutes les librairies Python listées dans requirements.txt
# --no-cache-dir : ne stocke pas le cache pip dans l'image (réduit la taille)
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code source de l'API dans le conteneur
COPY . .

# Indique que le conteneur écoute sur le port 8000 (documentation, ne publie pas le port)
EXPOSE 8000

# Commande lancée au démarrage du conteneur :
# uvicorn = serveur ASGI pour FastAPI
# app.main:app = fichier app/main.py, variable "app"
# --host 0.0.0.0 = écoute sur toutes les interfaces réseau (pas seulement localhost)
# --port 8000 = port d'écoute
# Note : docker-compose.yml surcharge cette commande avec --reload pour le développement
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
