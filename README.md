# MSPR TPRE502 - Projet de Mise en Situation Professionnelle

## 📋 Description du projet

Projet MSPR développé avec une architecture moderne utilisant :
- **Base de données** : Supabase (PostgreSQL)
- **API** : FastAPI avec documentation OpenAPI automatique
- **Interface web** : Next.js (App Router)
- **ETL** : Python + Pandas + SQLAlchemy
- **Orchestration** : Docker & Docker Compose

## 🏗️ Architecture

```
MSPR1/
├── api/                    # Service FastAPI
│   ├── app/
│   │   ├── main.py        # Point d'entrée FastAPI
│   │   ├── core/          # Configuration et base de données
│   │   ├── api/           # Routes et endpoints
│   │   ├── models/        # Modèles de données
│   │   ├── schemas/       # Schémas Pydantic
│   │   └── utils/         # Utilitaires
│   ├── Dockerfile
│   └── requirements.txt
│
├── web/                   # Interface Next.js
│   ├── src/app/          # Pages et route proxy `/api/mspr/*` → FastAPI
│   ├── Dockerfile
│   └── package.json
│
├── etl/                   # Pipeline ETL
│   ├── extract.py        # Extraction des données
│   ├── transform.py      # Transformation des données
│   ├── load.py           # Chargement dans Supabase
│   ├── scheduler.py      # Planificateur ETL
│   ├── data/             # Données sources
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml     # Configuration Docker
├── .env.example          # Exemple de variables d'environnement
├── .gitignore
└── README.md
```

## 🚀 Démarrage rapide

### Prérequis

- Docker et Docker Compose installés
- Compte Supabase créé
- Variables d'environnement configurées

### Installation

1. **Cloner le projet** (si applicable)
   ```bash
   git clone <repository-url>
   cd MSPR1
   ```

2. **Configurer les variables d'environnement**
   ```bash
   cp .env.example .env
   ```
   
   Éditez le fichier `.env` et remplissez vos credentials Supabase :
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-role-key
   DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
   JWT_SECRET=your-jwt-secret-key
   ETL_SCHEDULE=0 */6 * * *
   ```

3. **Construire et démarrer les services**
   ```bash
   docker-compose up --build
   ```

4. **Accéder aux services**
   - **API FastAPI** : http://localhost:8001 (port hôte mappé dans `docker-compose.yml`)
   - **Documentation API** : http://localhost:8001/docs
   - **Interface web (Docker)** : http://localhost:8000 par défaut — si tu vois un autre JSON sur un port, c’est une autre appli ; l’API MSPR est sur **8001**
   - **Interface web (`npm run dev` dans `web/`)** : http://localhost:3000

## 📚 Documentation des services

### API FastAPI

L'API FastAPI est exposée sur le port **8001** côté hôte dans ce dépôt (`8001:8000`). La documentation interactive est sur `/docs`.

#### Endpoints disponibles

- `GET /` - Page d'accueil
- `GET /health` - Vérification de santé
- `GET /api/v1/health` - Health check API
- `GET /api/v1/example` - Exemple d'endpoint

#### Ajouter un nouvel endpoint

1. Créer un nouveau fichier dans `api/app/api/v1/endpoints/`
2. Créer le router avec vos endpoints
3. Ajouter le router dans `api/app/api/v1/api.py`

### Interface web (Next.js)

L'interface est servie sur le port **3000**. Les appels API passent par le proxy interne ` /api/mspr/* ` (voir `web/src/app/api/mspr/`), configuré avec `API_URL` (souvent `http://api:8000` dans Docker).

#### Développement local sans Docker pour le front

```bash
cd web
cp .env.example .env.local   # ajuster API_URL (ex. http://127.0.0.1:8001)
npm install
npm run dev
```

#### Ajouter une page

1. Créer un fichier sous `web/src/app/(dashboard)/`
2. Utiliser `apiFetch` depuis `web/src/lib/api.ts` pour appeler l'API via le proxy

### Pipeline ETL

Le pipeline ETL s'exécute automatiquement selon le planning défini dans `ETL_SCHEDULE`.

#### Structure ETL

1. **Extract** (`extract.py`) : Extraction des données depuis diverses sources
2. **Transform** (`transform.py`) : Transformation et nettoyage des données
3. **Load** (`load.py`) : Chargement des données dans Supabase

#### Personnaliser le pipeline

Éditez la fonction `run_etl_pipeline()` dans `etl/scheduler.py` pour définir votre processus ETL.

#### Exécution manuelle

Pour tester le pipeline ETL manuellement :
```bash
docker-compose exec etl python scheduler.py
```

## 🛠️ Développement

### Structure du code

- **API** : Architecture modulaire avec séparation des routes, modèles et utilitaires
- **Next.js** : interface avec authentification JWT (stockage local) et proxy vers FastAPI
- **ETL** : Pipeline modulaire Extract-Transform-Load

### Ajout de dépendances

1. Ajouter la dépendance dans le `requirements.txt` approprié
2. Reconstruire le conteneur Docker :
   ```bash
   docker-compose build --no-cache <service>
   docker-compose up <service>
   ```

### Tests

Les tests peuvent être ajoutés dans chaque service :
- `api/tests/` pour les tests de l'API
- tests front : à ajouter sous `web/` si besoin
- `etl/tests/` pour les tests ETL

## 📝 Variables d'environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SUPABASE_URL` | URL de votre projet Supabase | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Clé anonyme Supabase | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `SUPABASE_SERVICE_KEY` | Clé service role Supabase | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://postgres:pass@...` |
| `JWT_SECRET` | Secret pour JWT | `your-secret-key` |
| `ETL_SCHEDULE` | Planning ETL (format cron) | `0 */6 * * *` |
| `API_URL` | URL de l'API pour le **conteneur web** (proxy serveur) | `http://api:8000` |

## 🧪 Tests

Des scripts de test sont disponibles dans le dossier `test/` :

```bash
# Test de configuration globale
./test/test_config.sh

# Test de connexion Supabase
python3 test/supabase/test_supabase_connection.py
```

Voir `test/README.md` pour plus de détails.

## 🐳 Commandes Docker utiles

```bash
# Démarrer tous les services
docker-compose up

# Démarrer en arrière-plan
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Reconstruire les images
docker-compose build --no-cache

# Redémarrer un service spécifique
docker-compose restart <service>

# Exécuter une commande dans un conteneur
docker-compose exec <service> <command>
```

## 📊 Supabase

### Configuration de la base de données

1. Créer les tables nécessaires dans Supabase
2. Configurer les politiques RLS (Row Level Security)
3. Tester les connexions depuis l'API

### Migration de schéma

Utilisez l'interface Supabase ou des migrations SQL pour gérer le schéma de base de données.

## 🔒 Sécurité

- Les variables d'environnement sensibles ne doivent jamais être commitées
- Utilisez les politiques RLS de Supabase pour la sécurité des données
- Validez toutes les entrées utilisateur dans l'API
- Utilisez HTTPS en production

## 📈 Améliorations futures

- [ ] Ajouter des tests unitaires et d'intégration
- [ ] Implémenter l'authentification complète
- [ ] Ajouter la gestion des erreurs avancée
- [ ] Optimiser les performances de l'ETL
- [ ] Ajouter des métriques et monitoring
- [ ] Déploiement en production (CI/CD)



