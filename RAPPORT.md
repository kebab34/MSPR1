# RAPPORT TECHNIQUE — MSPR TPRE501
## HealthAI Coach — Backend Métier

**Équipe** : Sarah Nizar, Natael Ozturk, Nassim Ghoulane  
**Formation** : CDA — EPSI | **Année** : 2025-2026

---

## 01. Introduction

### 1.1 Introduction

Dans le cadre du module TPRE501, nous avons réalisé une mise en situation professionnelle consistant à concevoir et développer l'infrastructure backend d'une plateforme de santé connectée. Ce projet nous a permis de mobiliser l'ensemble des compétences acquises en développement backend, gestion de bases de données, conception d'API et traitement de données.

L'objectif principal était de livrer un système complet capable de collecter des données hétérogènes provenant de sources variées, de les transformer, de les stocker dans une base relationnelle, et de les exposer via une API REST sécurisée accompagnée d'un dashboard de visualisation.

### 1.2 L'équipe

Le projet a été réalisé par une équipe de trois développeurs :

- **Sarah Nizar** — Base de données & Supabase  
  Sarah a pris en charge la modélisation et la mise en place de la base de données. Elle a conçu le schéma relationnel (11 tables, index, triggers), rédigé les migrations SQL et configuré l'instance Supabase locale. Elle a également géré le pipeline ETL : extraction des sources Kaggle et de l'API ExerciseDB, transformation des données et chargement dans Supabase via des scripts d'upsert.

- **Natael Ozturk** — Interface d'administration & Dashboard  
  Natael a développé l'intégralité de l'interface Streamlit avec ses 7 pages de visualisation (utilisateurs, aliments, exercices, journal alimentaire, sessions sport, mesures biométriques, analytics). Il a également assuré la configuration Docker Compose pour l'orchestration des services et la mise en place de l'environnement de développement local.

- **Nassim Ghoulane** — API REST & authentification  
  Nassim a conçu et développé l'API FastAPI, en structurant l'architecture par ressource (routes, schémas Pydantic, accès base de données). Il a mis en place le système d'authentification JWT complet (register, login, middleware de vérification des tokens) ainsi que la suite de 35 tests pytest couvrant l'ensemble des endpoints.

### 1.3 Contexte du projet

**HealthAI Coach** est une startup française spécialisée dans la santé connectée et le coaching personnalisé. Face à une croissance rapide de leur base utilisateurs, l'entreprise souhaitait mettre en place une infrastructure technique robuste pour collecter, transformer et stocker des données hétérogènes provenant de sources variées.

La mission qui nous a été confiée était de livrer un backend métier complet incluant :
- Un pipeline de collecte et traitement automatisé des données
- Une base de données relationnelle adaptée aux besoins métier
- Une API REST sécurisée pour exposer les données
- Une interface d'administration pour visualiser les indicateurs clés

---

## 02. Choix technologiques

### 2.1 Langage & Framework backend

Nous avons choisi **Python** comme langage principal pour l'ensemble du projet, pour sa maturité dans le domaine de la data et la richesse de son écosystème.

Pour le framework backend, notre choix s'est porté sur **FastAPI** pour plusieurs raisons :
- Support natif de l'asynchrone pour de hautes performances
- Validation automatique des données via Pydantic
- Génération automatique de la documentation OpenAPI (Swagger UI)
- Syntaxe moderne avec les type hints Python

### 2.2 Base de données

Nous avons opté pour **Supabase**, une plateforme open source construite sur **PostgreSQL**, qui offre :
- Une authentification intégrée avec gestion JWT
- Une API REST automatique sur les tables
- Row Level Security (RLS) pour la sécurité des données
- Une interface d'administration web
- Un déploiement local via Docker pour le développement

Le schéma compte **11 tables** relationnelles couvrant l'ensemble du domaine métier.

### 2.3 Pipeline ETL & traitement des données

Le pipeline ETL a été développé en Python avec **Pandas** pour la manipulation des données. Il intègre **APScheduler** pour l'exécution automatique toutes les 6 heures. L'architecture suit le pattern classique Extract → Transform → Load, avec une gestion robuste des erreurs par source de données.

### 2.4 API REST

L'API expose 7 ressources via des endpoints REST et implémente une authentification JWT complète. La documentation interactive est générée automatiquement et accessible sur `/docs`. Les routes sensibles sont protégées par un middleware de vérification de token Bearer.

### 2.5 Interface d'administration & Dashboard

L'interface d'administration a été développée avec **Streamlit**, un framework Python permettant de créer rapidement des applications web de visualisation de données. Ce choix nous a permis de livrer une interface fonctionnelle sans développement frontend complexe, avec 7 pages couvrant l'ensemble des ressources du système.

### 2.6 Sources de données retenues

Quatre sources de données ont été intégrées dans le pipeline :

| Source | Type | Données extraites |
|--------|------|-------------------|
| ExerciseDB (GitHub public) | API REST | 200 exercices sportifs |
| Daily Food & Nutrition | Kaggle CSV | 500 aliments + macronutriments |
| Gym Members Exercise | Kaggle CSV | Profils utilisateurs + mesures biométriques |
| Diet Recommendations | Kaggle CSV | 1 000 profils utilisateurs supplémentaires |

---

## 03. Architecture & Flux de données

### 3.1 Vue d'ensemble de l'architecture

Le projet s'articule autour de quatre composants containerisés et orchestrés via **Docker Compose** :

```
Sources externes (Kaggle CSV + API)
            ↓
    ┌───────────────┐
    │  Pipeline ETL │  → Collecte, nettoie, charge
    └───────┬───────┘
            ↓
    ┌───────────────┐
    │   Supabase    │  → PostgreSQL (11 tables)
    └───────┬───────┘
            ↓
    ┌───────────────┐
    │  API FastAPI  │  → REST sécurisé + JWT
    └───────┬───────┘
            ↓
    ┌───────────────┐
    │   Streamlit   │  → Interface d'administration
    └───────────────┘
```

Chaque composant est **indépendant et conteneurisé**, communiquant via un réseau Docker dédié (`mspr_network`).

### 3.2 Pipeline de collecte et ingestion

Le pipeline démarre automatiquement au lancement du conteneur ETL et s'exécute selon le planning défini (toutes les 6 heures). Pour chaque source, le processus est le suivant :

1. **Extraction** : lecture des fichiers CSV ou appel API
2. **Validation** : vérification de la présence des colonnes obligatoires
3. **Transformation** : nettoyage et normalisation des données
4. **Chargement** : upsert dans Supabase avec gestion des conflits

Les données sont traitées par **batches de 100 enregistrements** pour respecter les limites de l'API Supabase.

### 3.3 Processus de nettoyage et transformation

La phase de transformation applique plusieurs traitements successifs :
- **Suppression des doublons** et valeurs nulles critiques
- **Normalisation** des types de données (float, int, string)
- **Génération d'emails synthétiques** uniques pour les utilisateurs issus des datasets
- **Standardisation** des unités et formats de date
- **Restauration des colonnes liste** (objectifs utilisateurs stockés en tableau PostgreSQL)
- **Mapping email → UUID** pour établir les relations entre tables lors du chargement des mesures biométriques

### 3.4 Modèle de données relationnel

Le modèle de données couvre l'ensemble du domaine santé/sport avec 11 tables relationnelles :

```
utilisateurs ──┬── journal_alimentaire ──── aliments
               │                         └── recette_aliments ── recettes
               ├── sessions_sport ─────────── session_exercices ── exercices
               ├── mesures_biometriques
               ├── progressions ──────────── exercices
               └── objectifs
```

Les tables principales sont :
- **utilisateurs** : profil complet (âge, poids, taille, objectifs, type d'abonnement)
- **aliments** : catalogue nutritionnel (calories, protéines, glucides, lipides, fibres)
- **exercices** : bibliothèque sportive (type, groupe musculaire, niveau, équipement)
- **journal_alimentaire** : suivi quotidien des repas par utilisateur
- **sessions_sport** : historique des entraînements avec intensité et durée
- **mesures_biometriques** : suivi poids, fréquence cardiaque, sommeil, calories brûlées
- **progressions** : évolution des performances sur les exercices

### 3.5 Exposition via API

L'API FastAPI expose les données via des endpoints RESTful organisés par ressource. L'authentification repose sur **JWT Supabase** :

```
POST /api/v1/auth/register   →  Création de compte
POST /api/v1/auth/login      →  Authentification, retourne un token JWT
GET  /api/v1/auth/me         →  Profil de l'utilisateur connecté

GET/POST/PUT/DELETE /api/v1/utilisateurs
GET/POST/PUT/DELETE /api/v1/aliments
GET/POST/PUT/DELETE /api/v1/exercices
GET/POST/PUT/DELETE /api/v1/journal       (écriture protégée par JWT)
GET/POST/PUT/DELETE /api/v1/sessions      (écriture protégée par JWT)
GET/POST/PUT/DELETE /api/v1/mesures       (écriture protégée par JWT)
```

---

## 04. Bilan du projet, difficultés & perspectives

### 4.1 Résultats obtenus

#### 4.1.1 Pipeline ETL fonctionnel

Le pipeline ETL intègre les 4 sources de données et s'exécute automatiquement toutes les 6 heures. Il charge avec succès exercices, aliments et profils utilisateurs dans Supabase, avec une gestion des conflits par upsert pour éviter les doublons. Un script de seed complète la base avec des données synthétiques cohérentes.

#### 4.1.2 Base de données peuplée et validée

La base de données contient à l'issue du seed :

| Table | Volume |
|-------|--------|
| Utilisateurs | 200 profils |
| Aliments | 500 entrées |
| Exercices | 200 exercices |
| Journal alimentaire | 3 000 entrées |
| Sessions sport | 800 sessions |
| Exercices liés aux sessions | 2 348 liens |
| Progressions | 400 entrées |

#### 4.1.3 API REST opérationnelle

L'API répond correctement sur l'ensemble des 7 ressources. L'authentification JWT est fonctionnelle (register, login, vérification du token). La suite de **35 tests pytest** valide le comportement de tous les endpoints, avec un taux de réussite de **100%**.

#### 4.1.4 Dashboard et indicateurs clés

L'interface Streamlit est accessible sur le port 8501 et présente les données en temps réel via 7 pages : gestion des utilisateurs, catalogue alimentaire, bibliothèque d'exercices, journal alimentaire, sessions sport, mesures biométriques et analytics.

---

### 4.2 Difficultés rencontrées & Solutions apportées

#### 4.2.1 Problèmes liés aux sources de données

Les datasets Kaggle présentaient plusieurs problèmes de qualité : valeurs manquantes, colonnes mal typées, formats de dates inconsistants et absence d'identifiants uniques. Nous avons résolu ces problèmes en développant une chaîne de transformation robuste dans `transform.py`, avec génération d'emails synthétiques uniques et normalisation systématique des types.

Un autre problème était l'absence de lien entre les données biométriques et les utilisateurs dans le dataset Gym Members. Nous avons mis en place un mapping email → UUID en deux passes : d'abord insertion des utilisateurs, puis récupération de leurs UUIDs pour associer les mesures biométriques.

#### 4.2.2 Difficultés techniques

La principale difficulté technique a été la configuration réseau Docker. Les conteneurs ne pouvaient pas atteindre le Supabase local tournant sur la machine hôte via `localhost`. Nous avons résolu ce problème en utilisant `host.docker.internal` comme adresse dans les variables d'environnement, ce qui permet aux conteneurs Docker d'accéder aux services de la machine hôte sur Windows.

Nous avons également rencontré des problèmes lors de l'installation du CLI Supabase (non supporté via npm sur Windows), résolus en passant par le gestionnaire de paquets Scoop.

#### 4.2.3 Gestion du travail en équipe

La coordination entre les trois membres de l'équipe a nécessité une organisation rigoureuse du travail avec Git. Nous avons adopté une convention de commits claire (`feat:`, `fix:`, `refactor:`) et une séparation des responsabilités par composant pour limiter les conflits. Les revues de code régulières nous ont permis de maintenir une cohérence sur l'ensemble du projet.

---

### 4.3 Perspectives d'évolution

#### 4.3.1 Améliorations techniques envisagées

Plusieurs axes d'amélioration technique ont été identifiés :
- **RLS Supabase** : mettre en place les politiques de Row Level Security pour que chaque utilisateur n'accède qu'à ses propres données
- **CI/CD** : pipeline GitHub Actions pour automatiser les tests et le déploiement à chaque push
- **Pagination avancée** : enrichir les réponses API avec les métadonnées de pagination (`total`, `has_more`)
- **Tests ETL** : étendre la suite de tests au pipeline de transformation avec des fixtures CSV

#### 4.3.2 Intégration des modules IA

Les données collectées constituent une base solide pour intégrer des fonctionnalités d'intelligence artificielle :
- **Recommandations nutritionnelles** : suggérer des repas adaptés aux objectifs et au profil de l'utilisateur
- **Planification d'entraînements** : générer des programmes sportifs personnalisés basés sur l'historique de sessions et les progressions
- **Détection d'anomalies** : alerter sur des variations inhabituelles des mesures biométriques (fréquence cardiaque, poids)

#### 4.3.3 Scalabilité et déploiement en production

Pour un passage en production, plusieurs évolutions seraient nécessaires :
- Migration vers un Supabase cloud avec réplication et sauvegardes automatiques
- Mise en place d'un reverse proxy (Nginx) avec HTTPS
- Monitoring des performances via Prometheus et Grafana
- Déploiement sur infrastructure cloud (AWS, GCP ou Azure) avec auto-scaling

---

## 05. Conclusion

### 5.1 Conclusion

Ce projet MSPR nous a permis de concevoir et livrer une infrastructure backend complète répondant aux besoins de HealthAI Coach. De la collecte des données brutes jusqu'à leur exposition via une API sécurisée et un dashboard de visualisation, chaque composant a été pensé pour être modulaire, testable et déployable.

Les principaux apprentissages portent sur l'intégration de sources de données hétérogènes, la conception d'une API REST sécurisée avec authentification JWT, la mise en place de tests automatisés, et la conteneurisation d'une application multi-services avec Docker.

Le projet constitue une base solide et évolutive sur laquelle HealthAI Coach pourra développer ses futures fonctionnalités de coaching personnalisé, notamment l'intégration de modules d'intelligence artificielle pour la recommandation et la personnalisation.

---

*Projet réalisé dans le cadre du MSPR TPRE501 — CDA EPSI 2025-2026*  
*Sarah Nizar • Natael Ozturk • Nassim Ghoulane*
