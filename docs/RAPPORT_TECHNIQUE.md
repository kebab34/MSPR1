# Rapport Technique — HealthAI Coach Backend

## Projet MSPR TPRE501 — Bloc E6.1

**Équipe projet** : MSPR TPRE501  
**Date** : Avril 2026  
**Version** : 2.0

---

## 1. Contexte et Objectifs

### 1.1. Contexte

HealthAI Coach est une startup française positionnée sur le marché de la santé connectée et du coaching personnalisé. L'entreprise souhaite mettre en place une infrastructure technique robuste pour collecter, transformer et stocker des données hétérogènes provenant de sources variées (APIs publiques, datasets open data, fichiers simulés).

### 1.2. Objectifs

L'objectif principal était de concevoir, développer et livrer le backend métier de la future plateforme HealthAI Coach, incluant :

- Un système de collecte automatisée capable d'intégrer différentes sources de données
- Un processus de transformation et de nettoyage garantissant l'exploitabilité des données
- Une base de données relationnelle adaptée aux besoins de l'entreprise
- Une API REST permettant de consulter et d'exploiter les données consolidées
- Une interface web accessible permettant de suivre les indicateurs clés

---

## 2. Choix Technologiques

### 2.1. Architecture Générale

L'architecture choisie suit une approche modulaire en trois services Docker indépendants :

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   ETL       │────▶│     Supabase     │◀────│    API      │
│  Pipeline   │     │   (PostgreSQL)   │     │  (FastAPI)  │
└─────────────┘     └──────────────────┘     └──────┬──────┘
                                                     │ HTTP
                                                     ▼
                                             ┌─────────────┐
                                             │  Next.js    │
                                             │  Interface  │
                                             └─────────────┘
```

Le frontend Next.js communique exclusivement avec l'API FastAPI via un proxy interne (`/api/mspr`) — jamais directement avec Supabase. Cela garantit que toute la logique d'autorisation passe par l'API.

### 2.2. Technologies Retenues

#### 2.2.1. Base de Données : Supabase (PostgreSQL)

**Justification** :
- PostgreSQL offre robustesse et performances adaptées aux besoins relationnels
- Supabase fournit une infrastructure hébergée avec authentification JWT intégrée
- Support natif des types complexes (arrays, JSONB, UUID)
- Interface d'administration et SQL Editor intégrés

#### 2.2.2. API : FastAPI (Python)

**Justification** :
- Framework moderne et performant (Starlette + Pydantic)
- Documentation OpenAPI automatique accessible sur `/docs` et `/redoc`
- Validation des données intégrée via Pydantic v2
- Support asynchrone natif, type hints pour la maintenabilité

#### 2.2.3. Interface Web : Next.js 15 + React 19

**Justification** :
- Framework React avec rendu hybride (SSR/CSR) et routage intégré
- Tailwind CSS v4 pour un design système cohérent et accessible
- Proxy interne (`/api/mspr`) évitant l'exposition directe de l'API au navigateur
- Contrôle total sur le HTML généré (contrairement à Streamlit) permettant la conformité RGAA

**Avantages par rapport à une solution Python-only** :
- Séparation claire frontend/backend
- Expérience utilisateur réactive (pas de rechargement de page)
- Accessibilité numérique contrôlable (RGAA AA)
- Déploiement indépendant des services

#### 2.2.4. Pipeline ETL : Python + Pandas + APScheduler

**Justification** :
- Pandas est la bibliothèque standard pour la manipulation de données
- APScheduler permet la planification cron en pur Python sans dépendance externe
- Architecture modulaire : `extract.py`, `transform.py`, `load.py`

#### 2.2.5. Orchestration : Docker & Docker Compose

**Justification** :
- Environnement reproductible sur toute machine disposant de Docker
- Isolation des services (api, web, etl)
- Déploiement en une commande (`docker-compose up -d`)

---

## 3. Architecture Détaillée

### 3.1. Modèle de Données

Le modèle de données suit une approche relationnelle avec 11 tables :

| Table | Rôle |
|---|---|
| `utilisateurs` | Profils utilisateurs, rôles, abonnements |
| `aliments` | Base nutritionnelle (calories, macronutriments) |
| `exercices` | Catalogue d'exercices sportifs |
| `journal_alimentaire` | Suivi nutritionnel quotidien |
| `sessions_sport` | Sessions d'entraînement |
| `session_exercices` | Exercices réalisés par session (table associative) |
| `mesures_biometriques` | Données de santé (poids, FC, sommeil) |
| `objectifs` | Objectifs personnalisés des utilisateurs |
| `progressions` | Suivi des progressions sur exercice |
| `recettes` | Recettes nutritionnelles |
| `recette_aliments` | Composition des recettes (table associative) |

La documentation complète est disponible dans `docs/MCD.txt`, `docs/MLD.txt` et `docs/MPD.md`.

### 3.2. Pipeline ETL

Le pipeline ETL suit l'architecture classique Extract-Transform-Load :

1. **Extract** : Extraction depuis ExerciseDB API et 3 datasets Kaggle (CSV)
2. **Transform** : Nettoyage, normalisation, validation (`transform.py`)
3. **Load** : Chargement dans Supabase avec upsert (gestion des conflits)

**Planification** : APScheduler avec expression cron configurable via `ETL_SCHEDULE` (défaut : `0 2 * * 1` = lundi 02h00 UTC). Le pipeline s'exécute également immédiatement au démarrage du conteneur.

**Logs** : Chaque exécution produit :
- Un fichier log rotatif journalier dans `etl/logs/etl_YYYY-MM-DD.log`
- Un rapport JSON dans `etl/logs/reports/report_YYYY-MM-DD_HH-MM-SS.json` (statut, durée, lignes chargées, erreurs par source)

### 3.3. API REST

L'API FastAPI expose des endpoints CRUD complets avec contrôle d'accès basé sur les rôles (user/admin) :

| Méthode | Pattern | Description |
|---|---|---|
| GET | `/api/v1/{entité}` | Liste paginée avec filtres |
| GET | `/api/v1/{entité}/{id}` | Détail d'un enregistrement |
| POST | `/api/v1/{entité}` | Création |
| PUT | `/api/v1/{entité}/{id}` | Mise à jour partielle |
| DELETE | `/api/v1/{entité}/{id}` | Suppression |

**Sécurité** : JWT Supabase vérifié à chaque requête via `get_current_profile` (middleware). Les utilisateurs non-admin ne voient que leurs propres données (filtre forcé côté serveur).

**Documentation** : OpenAPI interactive sur `http://localhost:8001/docs`.

### 3.4. Interface Web Next.js

L'interface propose :

- **Accueil** : Statistiques globales, accès rapide aux fonctionnalités
- **Journal alimentaire** : Saisie avec recherche d'aliments par nom, historique, export CSV
- **Sessions sport** : Enregistrement de séances avec sélection d'exercices (séries/reps/poids), export CSV
- **Mesures biométriques** : Saisie et historique des indicateurs de santé, export CSV
- **Aliments** : Catalogue searchable avec filtres
- **Exercices** : Catalogue avec filtres type/muscle/niveau/équipement
- **Profil** : Gestion du profil utilisateur
- **Utilisateurs** (admin) : Gestion et recherche des comptes
- **Analytics** (admin) : Tableau de bord avec KPIs et distribution des données

---

## 4. Résultats Obtenus

### 4.1. Fonctionnalités Implémentées

✅ **Pipeline ETL opérationnel** :
- Extraction depuis ExerciseDB API (200 exercices)
- Extraction depuis 3 datasets Kaggle (aliments, utilisateurs, mesures)
- Téléchargement automatique des datasets si absents
- Logs fichiers + rapports JSON par exécution
- Planification APScheduler configurable

✅ **Base de données relationnelle** :
- 11 tables avec relations, contraintes et index
- Scripts SQL de migration versionnés (`supabase/migrations/`)
- MCD, MLD et MPD documentés

✅ **API REST complète** :
- Endpoints CRUD pour toutes les entités
- Authentification JWT et contrôle d'accès par rôle
- Documentation OpenAPI interactive
- Tests automatisés (pytest + mock Supabase)

✅ **Interface web accessible** :
- Design responsive (mobile + desktop)
- Export CSV (journal, sessions, mesures)
- Suppression depuis l'UI avec confirmation
- Conformité RGAA AA documentée
- Authentification (login + inscription)

### 4.2. Métriques

- **Temps d'exécution ETL** : ~30–60 secondes (200 exercices + datasets Kaggle)
- **Temps de réponse API** : < 200ms pour la plupart des requêtes
- **Taux de réussite ETL** : > 95% (gestion des erreurs par source isolée)
- **Volume de données** : 200+ exercices, 500+ aliments, 1000+ utilisateurs (datasets Kaggle)

---

## 5. Difficultés Rencontrées et Solutions

### 5.1. Sérialisation des dates Python → JSON

**Problème** : `model_dump()` de Pydantic retourne des objets `datetime` Python non sérialisables par le client Supabase.

**Solution** : Utilisation de `model_dump(mode="json")` qui convertit les datetimes en chaînes ISO 8601 avant l'insertion.

### 5.2. Gestion des conflits lors du chargement ETL

**Problème** : Les datasets contiennent des doublons causant des erreurs d'insertion.

**Solution** : Upsert basé sur clés uniques (`nom` pour exercices/aliments, `email` pour utilisateurs).

### 5.3. Validation des données hétérogènes

**Problème** : Formats différents selon les sources (colonnes, types, encodages).

**Solution** : Fonctions de transformation spécifiques par source dans `transform.py`, normalisation vers un schéma commun.

### 5.4. Accessibilité et choix du framework frontend

**Problème** : Streamlit (solution initiale) ne permettait pas de contrôler le HTML généré, rendant la conformité RGAA impossible.

**Solution** : Migration vers Next.js 15, permettant le contrôle total des balises sémantiques, attributs ARIA et contrastes.

---

## 6. Perspectives d'Évolution

### 6.1. Court Terme

- **ARIA complets** : Ajouter `aria-hidden` sur les icônes décoratives, rôles `combobox`/`listbox` sur les dropdowns
- **Modules IA** : Recommandations nutritionnelles et sportives personnalisées
- **Monitoring** : Tableau de bord de santé ETL visible dans l'interface admin

### 6.2. Moyen Terme

- **Cache Redis** : Pour les endpoints les plus sollicités (listes aliments/exercices)
- **Notifications push** : Rappels journalier de saisie
- **Intégration objets connectés** : Import automatique des données biométriques

### 6.3. Long Terme

- **Scalabilité** : Migration vers une architecture microservices
- **Data Warehouse** : Entrepôt de données pour l'analytics avancé
- **Multi-tenant B2B** : Isolation des données par client

---

## 7. Conclusion

Le projet a permis de mettre en place un backend métier complet et fonctionnel pour HealthAI Coach. L'architecture modulaire (ETL + API FastAPI + Interface Next.js + Supabase) est reproductible en une commande Docker et respecte les bonnes pratiques de développement. La migration de Streamlit vers Next.js a permis d'atteindre un niveau d'accessibilité conforme aux exigences RGAA AA.

---

## 8. Annexes

### 8.1. Structure du Projet

```
MSPR1/
├── api/                    # Service FastAPI (Python)
├── web/                    # Interface Next.js (TypeScript)
├── etl/                    # Pipeline ETL (Python + Pandas)
│   ├── logs/               # Logs et rapports d'exécution
│   └── data/               # Datasets CSV
├── docs/                   # Documentation complète
├── supabase/migrations/    # Scripts SQL versionnés
├── test/                   # Tests automatisés (pytest)
└── docker-compose.yml      # Orchestration Docker
```

### 8.2. Documentation Complémentaire

- `docs/RAPPORT_INVENTAIRE_SOURCES.md` : Inventaire des sources de données
- `docs/DIAGRAMME_FLUX_DONNEES.md` : Diagramme des flux de données
- `docs/API_ENDPOINTS.md` : Documentation des endpoints API
- `docs/MCD.txt`, `docs/MLD.txt`, `docs/MPD.md` : Modèles de données
- `docs/AUDIT_RGAA.md` : Audit accessibilité RGAA AA

### 8.3. Technologies Utilisées

| Composant | Technologie | Version |
|---|---|---|
| Base de données | PostgreSQL via Supabase | 15+ |
| API | FastAPI + Pydantic v2 | 0.104+ |
| Interface web | Next.js + React | 15 / 19 |
| CSS | Tailwind CSS | v4 |
| ETL | Python + Pandas | 3.10+ / 2.1+ |
| Planification | APScheduler | 3.10+ |
| Orchestration | Docker + Docker Compose | 24+ / 2.20+ |
| Tests | pytest | 7+ |

---

**Document généré le** : Avril 2026  
**Version** : 2.0  
**Auteur** : Équipe MSPR TPRE501
