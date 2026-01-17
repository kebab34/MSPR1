# 🚀 Guide de Déploiement - HealthAI Coach Backend

## HealthAI Coach - Backend Métier

**Version** : 1.0  
**Date** : 2025

---

## 1. Prérequis

### 1.1. Logiciels Requis

- **Docker** : Version 24.0 ou supérieure
- **Docker Compose** : Version 2.20 ou supérieure
- **Git** : Pour cloner le repository (optionnel)
- **Python** : 3.10 ou supérieure (pour développement local sans Docker)

### 1.2. Compte Supabase

Un compte Supabase est nécessaire pour la base de données. Si vous n'en avez pas :

1. Créer un compte sur [https://supabase.com](https://supabase.com)
2. Créer un nouveau projet
3. Noter les informations suivantes :
   - URL du projet (ex: `https://xxxxx.supabase.co`)
   - Clé API anonyme (anon key)
   - Clé API service (service_role key)
   - JWT Secret (Legacy JWT Secret)

### 1.3. Variables d'Environnement

Les variables d'environnement suivantes sont requises :

- `SUPABASE_URL` : URL de votre projet Supabase
- `SUPABASE_KEY` : Clé API anonyme
- `SUPABASE_SERVICE_KEY` : Clé API service
- `JWT_SECRET` : JWT Secret (Legacy)
- `DATABASE_URL` : URL de connexion PostgreSQL (optionnel)
- `ETL_SCHEDULE` : Planification ETL (format cron, ex: `0 */6 * * *`)
- `API_URL` : URL de l'API (par défaut: `http://localhost:8000`)

---

## 2. Installation Rapide (Docker)

### 2.1. Cloner le Repository

```bash
git clone <repository-url>
cd MSPR1
```

### 2.2. Configurer les Variables d'Environnement

1. Copier le fichier d'exemple :
```bash
cp .env.example .env
```

2. Éditer le fichier `.env` et remplir les valeurs :

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
JWT_SECRET=your-jwt-secret

# Database (optionnel, Supabase fournit déjà l'URL)
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres

# ETL Schedule (cron format: toutes les 6 heures)
ETL_SCHEDULE=0 */6 * * *

# API URL
API_URL=http://localhost:8000
```

### 2.3. Construire et Démarrer les Services

```bash
# Construire les images Docker
docker-compose build

# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f
```

### 2.4. Vérifier le Déploiement

1. **API FastAPI** : http://localhost:8000
   - Documentation Swagger : http://localhost:8000/docs
   - Health check : http://localhost:8000/health

2. **Interface Streamlit** : http://localhost:8501

3. **Vérifier les logs** :
```bash
docker-compose logs api
docker-compose logs streamlit
docker-compose logs etl
```

---

## 3. Installation Manuelle (Sans Docker)

### 3.1. Prérequis Python

```bash
# Vérifier la version Python
python3 --version  # Doit être 3.10+

# Installer pip si nécessaire
python3 -m ensurepip --upgrade
```

### 3.2. Installation des Dépendances

#### API FastAPI

```bash
cd api
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Interface Streamlit

```bash
cd streamlit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Pipeline ETL

```bash
cd etl
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3.3. Configuration

1. Créer le fichier `.env` à la racine du projet (voir section 2.2)

2. Vérifier que les chemins dans `.env` sont corrects

### 3.4. Démarrer les Services

#### API FastAPI

```bash
cd api
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Interface Streamlit

```bash
cd streamlit
source venv/bin/activate
streamlit run app.py --server.port 8501
```

#### Pipeline ETL (manuel)

```bash
cd etl
source venv/bin/activate
python scheduler.py
```

#### Pipeline ETL (planifié avec cron)

```bash
# Éditer le crontab
crontab -e

# Ajouter la ligne (exécution toutes les 6 heures)
0 */6 * * * cd /chemin/vers/MSPR1/etl && /chemin/vers/python3 scheduler.py >> /var/log/etl.log 2>&1
```

---

## 4. Configuration de la Base de Données

### 4.1. Créer les Tables dans Supabase

1. **Via SQL Editor** (recommandé) :

   - Aller dans Supabase Dashboard → SQL Editor
   - Créer un nouveau script
   - Exécuter les scripts SQL de création des tables

   Les scripts SQL sont disponibles dans `docs/create_tables_example.sql` (à adapter selon votre schéma).

2. **Via Table Editor** :

   - Aller dans Supabase Dashboard → Table Editor
   - Créer les tables manuellement selon le MLD (voir `docs/MLD.txt`)

### 4.2. Vérifier la Connexion

```bash
# Tester la connexion (si Python installé)
python3 test/supabase/test_supabase_connection.py
```

---

## 5. Exécution du Pipeline ETL

### 5.1. Exécution Manuelle

```bash
cd etl
python scheduler.py
```

### 5.2. Exécution Planifiée

Le pipeline ETL est configuré pour s'exécuter automatiquement selon le planning défini dans `ETL_SCHEDULE` (format cron).

**Exemples de planification** :
- `0 */6 * * *` : Toutes les 6 heures
- `0 0 * * *` : Tous les jours à minuit
- `*/30 * * * *` : Toutes les 30 minutes

### 5.3. Vérifier les Logs ETL

```bash
# Avec Docker
docker-compose logs etl

# Sans Docker
tail -f /var/log/etl.log  # Si configuré avec cron
```

---

## 6. Accès aux Services

### 6.1. API FastAPI

- **URL** : http://localhost:8000
- **Documentation Swagger** : http://localhost:8000/docs
- **Documentation ReDoc** : http://localhost:8000/redoc
- **Health Check** : http://localhost:8000/health

### 6.2. Interface Streamlit

- **URL** : http://localhost:8501
- **Pages disponibles** :
  - Accueil : Statistiques globales
  - Dashboard : Graphiques et KPIs
  - Exercices : Gestion CRUD
  - Utilisateurs : Gestion CRUD
  - Aliments : Gestion CRUD
  - Configuration : Outils et export

---

## 7. Dépannage

### 7.1. Problèmes de Connexion Supabase

**Symptôme** : Erreur "Invalid API key" ou "Connection refused"

**Solutions** :
1. Vérifier les variables d'environnement dans `.env`
2. Vérifier que les clés API sont correctes dans Supabase Dashboard
3. Vérifier que le projet Supabase est actif

### 7.2. Problèmes Docker

**Symptôme** : Erreur "Cannot connect to Docker daemon"

**Solutions** :
1. Vérifier que Docker est démarré : `docker ps`
2. Vérifier les permissions : `sudo usermod -aG docker $USER` (Linux)
3. Redémarrer Docker

### 7.3. Problèmes de Port

**Symptôme** : "Port already in use"

**Solutions** :
1. Changer les ports dans `docker-compose.yml`
2. Arrêter les services utilisant les ports :
   ```bash
   # Trouver le processus
   lsof -i :8000  # Pour le port 8000
   # Tuer le processus
   kill -9 <PID>
   ```

### 7.4. Problèmes ETL

**Symptôme** : Erreurs lors de l'exécution du pipeline ETL

**Solutions** :
1. Vérifier les logs : `docker-compose logs etl`
2. Vérifier que les sources de données sont accessibles
3. Vérifier les permissions d'écriture dans Supabase
4. Exécuter manuellement pour voir les erreurs détaillées

---

## 8. Commandes Utiles

### 8.1. Docker Compose

```bash
# Démarrer les services
docker-compose up -d

# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs -f

# Reconstruire les images
docker-compose build --no-cache

# Redémarrer un service
docker-compose restart api

# Exécuter une commande dans un conteneur
docker-compose exec api bash
```

### 8.2. Maintenance

```bash
# Nettoyer les conteneurs arrêtés
docker-compose down --volumes

# Voir l'utilisation des ressources
docker stats

# Voir les images Docker
docker images
```

---

## 9. Déploiement en Production

### 9.1. Recommandations

1. **Sécurité** :
   - Utiliser HTTPS (certificat SSL)
   - Activer Row Level Security (RLS) dans Supabase
   - Limiter l'accès aux clés API service
   - Utiliser des variables d'environnement sécurisées

2. **Performance** :
   - Configurer un reverse proxy (Nginx, Traefik)
   - Mettre en place un cache (Redis)
   - Optimiser les requêtes SQL
   - Utiliser un CDN pour les assets statiques

3. **Monitoring** :
   - Configurer des logs centralisés
   - Mettre en place des alertes
   - Monitorer les performances (APM)
   - Surveiller l'utilisation des ressources

### 9.2. Variables d'Environnement en Production

Utiliser un gestionnaire de secrets (HashiCorp Vault, AWS Secrets Manager, etc.) plutôt que des fichiers `.env` en production.

---

## 10. Support

Pour toute question ou problème :

1. Consulter la documentation dans `docs/`
2. Vérifier les logs des services
3. Consulter la documentation des technologies utilisées :
   - [FastAPI](https://fastapi.tiangolo.com/)
   - [Streamlit](https://docs.streamlit.io/)
   - [Supabase](https://supabase.com/docs)
   - [Docker](https://docs.docker.com/)

---

## 11. Temps de Déploiement Estimé

- **Installation initiale** : 15-30 minutes
- **Configuration** : 10-15 minutes
- **Premier lancement ETL** : 1-2 minutes
- **Total** : **30-45 minutes**

---

**Document généré le** : 2025  
**Version** : 1.0  
**Auteur** : Équipe MSPR TPRE501

