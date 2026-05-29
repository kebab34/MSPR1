# Image de base : Python 3.11 en version "slim" (allégée, sans outils inutiles)
FROM python:3.11-slim

# Définit /app comme répertoire de travail dans le conteneur
WORKDIR /app

# Installe les dépendances système :
# - gcc : compilateur requis par certaines librairies Python
# - postgresql-client : outils PostgreSQL (utile pour déboguer la connexion à Supabase)
# rm -rf /var/lib/apt/lists/* : supprime le cache apt pour réduire la taille de l'image
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copie requirements.txt en premier pour profiter du cache Docker
# (si les dépendances ne changent pas, cette couche est réutilisée)
COPY requirements.txt .

# Installe toutes les librairies Python (pandas, apscheduler, supabase, etc.)
# --no-cache-dir : ne stocke pas le cache pip dans l'image
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code source de l'ETL dans le conteneur
COPY . .

# Crée le dossier /app/data où seront stockés les fichiers CSV Kaggle
# (le volume Docker dans docker-compose.yml monte etl/data/ ici)
RUN mkdir -p /app/data

# Commande lancée au démarrage : lance le scheduler ETL
# scheduler.py démarre le pipeline immédiatement puis le planifie selon ETL_SCHEDULE
CMD ["python", "scheduler.py"]
