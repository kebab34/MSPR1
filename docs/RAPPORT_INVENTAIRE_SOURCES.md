# 📊 Rapport d'Inventaire des Sources de Données

## HealthAI Coach - Backend Métier

**Date de création** : 2025  
**Version** : 1.0  
**Équipe projet** : MSPR TPRE501

---

## 1. Introduction

Ce document recense toutes les sources de données utilisées dans le projet HealthAI Coach, en précisant leur origine, leur format, leur fréquence de mise à jour et les règles appliquées pour en assurer la qualité.

---

## 2. Sources de Données Externes

### 2.1. ExerciseDB API (Exercices Sportifs)

**Origine** :  
- **Source principale** : Repository GitHub public `yuhonas/free-exercise-db`
- **URL** : `https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json`
- **Source alternative** : RapidAPI ExerciseDB (si clé API disponible)
- **Type** : Open Data / API publique

**Format** :  
- **Format de données** : JSON
- **Structure** : Tableau d'objets JSON
- **Encodage** : UTF-8

**Fréquence de mise à jour** :  
- **Mise à jour source** : Irrégulière (dépend du mainteneur GitHub)
- **Fréquence d'ingestion** : Toutes les 6 heures (configurable via `ETL_SCHEDULE`)
- **Stratégie** : Upsert basé sur le nom de l'exercice pour éviter les doublons

**Volume** :  
- **Nombre d'exercices disponibles** : ~1300+ exercices
- **Volume ingéré** : 200 exercices par exécution (limite configurable)
- **Taille moyenne** : ~50-100 KB par extraction

**Règles de qualité appliquées** :  
1. **Validation des champs obligatoires** :
   - `nom` : Requis, non vide, string
   - `type` : Normalisé (force, cardio, flexibilite, autre)
   - `niveau` : Normalisé (debutant, intermediaire, avance)
   - `equipement` : Normalisé (aucun, haltères, barre, etc.)

2. **Nettoyage** :
   - Suppression des doublons basée sur le nom
   - Normalisation des valeurs de type, niveau, équipement
   - Conversion des listes en chaînes de caractères pour compatibilité PostgreSQL
   - Gestion des valeurs nulles

3. **Transformation** :
   - Mapping des champs API vers le schéma base de données :
     - `name` → `nom`
     - `type` → `type` (normalisé)
     - `muscle` → `groupe_musculaire`
     - `difficulty` → `niveau` (normalisé)
     - `equipment` → `equipement` (normalisé)
     - `instructions` → `instructions`
   - Source marquée comme "ExerciseDB API"

**Justification du choix** :  
- Source gratuite et accessible sans authentification
- Données structurées et complètes (nom, type, groupe musculaire, niveau, équipement, instructions)
- Volume important permettant de couvrir une large gamme d'exercices
- Format JSON facilement exploitable
- Alternative disponible via RapidAPI si besoin d'accès premium

---

### 2.2. Datasets Kaggle (Nutrition)

**Origine** :  
- **Source 1** : Daily Food & Nutrition Dataset
  - **URL** : `https://www.kaggle.com/datasets/adilshamim8/daily-food-and-nutrition-dataset`
  - **Auteur** : adilshamim8
  - **Type** : Open Data (Kaggle)

- **Source 2** : Diet Recommendations Dataset
  - **URL** : `https://www.kaggle.com/datasets/ziya07/diet-recommendations-dataset`
  - **Auteur** : ziya07
  - **Type** : Open Data (Kaggle)

**Format** :  
- **Format de données** : CSV
- **Séparateur** : Virgule (`,`)
- **Encodage** : UTF-8
- **En-têtes** : Présents (première ligne)

**Fréquence de mise à jour** :  
- **Mise à jour source** : Statique (datasets Kaggle)
- **Fréquence d'ingestion** : Toutes les 6 heures (configurable)
- **Stratégie** : Upsert basé sur le nom de l'aliment

**Volume** :  
- **Volume estimé** : Variable selon le dataset (100-1000+ aliments)
- **Taille moyenne** : 1-5 MB par fichier CSV

**Règles de qualité appliquées** :  
1. **Validation des champs obligatoires** :
   - `nom` : Requis, non vide
   - `calories` : Requis, numérique, >= 0

2. **Nettoyage** :
   - Suppression des doublons
   - Normalisation des noms d'aliments (minuscules, suppression accents optionnelle)
   - Validation des valeurs nutritionnelles (calories, protéines, glucides, lipides >= 0)
   - Gestion des valeurs manquantes (remplacement par 0 pour valeurs numériques)

3. **Transformation** :
   - Mapping des colonnes selon le format source :
     - Standardisation des noms de colonnes
     - Conversion des unités (g, mg, etc.)
     - Normalisation des valeurs nutritionnelles
   - Source marquée selon le dataset d'origine

**Justification du choix** :  
- Données nutritionnelles complètes et vérifiées
- Format CSV standardisé et facilement exploitable
- Volume important permettant de couvrir une large gamme d'aliments
- Données open source accessibles gratuitement
- Compatibilité avec les outils ETL standards (Pandas)

---

### 2.3. Données Utilisateurs Simulées

**Origine** :  
- **Source** : Génération interne / Simulation
- **Type** : Données de test générées par le pipeline ETL

**Format** :  
- **Format de données** : Génération programmatique (Python)
- **Structure** : Dictionnaires Python convertis en DataFrame

**Fréquence de mise à jour** :  
- **Génération** : À chaque exécution du pipeline ETL (si données manquantes)
- **Stratégie** : Insertion uniquement si utilisateurs de test absents

**Volume** :  
- **Nombre d'utilisateurs de test** : 2-5 utilisateurs
- **Objectif** : Permettre les tests et démonstrations

**Règles de qualité appliquées** :  
1. **Validation** :
   - Email : Format valide (validation regex)
   - Âge : Entre 1 et 150 ans
   - Poids : > 0 kg
   - Taille : > 0 cm
   - Objectifs : Liste de strings valides

2. **Nettoyage** :
   - Normalisation des emails (minuscules)
   - Validation des types d'abonnement (freemium, premium, premium+, B2B)
   - Formatage des objectifs en tableau PostgreSQL

**Justification du choix** :  
- Nécessaire pour les tests et démonstrations
- Permet de valider le fonctionnement complet du système
- Données réalistes mais fictives (conformité RGPD)

---

## 3. Sources de Données Internes

### 3.1. Base de Données Supabase (PostgreSQL)

**Origine** :  
- **Source** : Base de données relationnelle Supabase
- **Type** : Base de données PostgreSQL hébergée

**Format** :  
- **Format de données** : PostgreSQL (relationnel)
- **Schéma** : Défini selon le MLD (Modèle Logique de Données)
- **Tables principales** :
  - `utilisateurs`
  - `objectifs`
  - `aliments`
  - `exercices`
  - `journal_alimentaire`
  - `sessions_sport`
  - `session_exercices`
  - `mesures_biometriques`
  - `progressions`

**Fréquence de mise à jour** :  
- **Mise à jour** : Continue (via API et ETL)
- **Fréquence d'ingestion** : En temps réel (API) + Batch (ETL toutes les 6h)

**Volume** :  
- **Volume actuel** : Variable selon les données ingérées
- **Capacité** : Illimitée (selon plan Supabase)

**Règles de qualité appliquées** :  
1. **Contraintes de base de données** :
   - Clés primaires (UUID)
   - Clés étrangères (intégrité référentielle)
   - Contraintes UNIQUE (emails, noms d'exercices/aliments)
   - Contraintes CHECK (valeurs numériques >= 0)

2. **Validation applicative** :
   - Validation via Pydantic schemas (API)
   - Validation via Pandas (ETL)
   - Gestion des erreurs et rollback en cas d'échec

---

## 4. Diagramme des Flux de Données

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCES DE DONNÉES EXTERNES                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  ExerciseDB API  │  │  Kaggle Datasets │  │  Données     │  │
│  │  (JSON)          │  │  (CSV)           │  │  Simulées    │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘  │
│           │                     │                    │          │
└───────────┼─────────────────────┼────────────────────┼──────────┘
            │                     │                    │
            ▼                     ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE ETL (EXTRACT)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • extract_exercises_from_exercisedb()                         │
│  • extract_from_csv()                                          │
│  • extract_from_excel()                                        │
│  • extract_from_api()                                          │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              PIPELINE ETL (TRANSFORM & CLEAN)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • transform_exercises_from_exercisedb()                        │
│  • transform_foods_from_csv()                                   │
│  • clean_data()                                                 │
│    - Suppression doublons                                       │
│    - Normalisation valeurs                                      │
│    - Validation types                                           │
│  • validate_data()                                              │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              PIPELINE ETL (LOAD)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • SupabaseLoader.upsert_dataframe()                           │
│  • Gestion des conflits (on_conflict)                           │
│  • Logging des erreurs                                         │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│         BASE DE DONNÉES SUPABASE (PostgreSQL)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Tables:                                                        │
│  • utilisateurs                                                 │
│  • objectifs                                                    │
│  • aliments                                                     │
│  • exercices                                                    │
│  • journal_alimentaire                                          │
│  • sessions_sport                                               │
│  • mesures_biometriques                                         │
│  • ...                                                          │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API REST (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Endpoints CRUD:                                                │
│  • GET    /api/v1/utilisateurs                                  │
│  • POST   /api/v1/utilisateurs                                  │
│  • PUT    /api/v1/utilisateurs/{id}                             │
│  • DELETE /api/v1/utilisateurs/{id}                             │
│  • ... (aliments, exercices, journal, sessions, mesures)        │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│         INTERFACE ADMINISTRATION (Streamlit)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • Dashboard avec visualisations                                │
│  • Outils de nettoyage interactifs                              │
│  • Export des données (JSON/CSV)                                │
│  • Gestion des données (CRUD)                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Règles de Qualité Globales

### 5.1. Validation des Données

1. **Validation des types** :
   - Vérification des types de données (string, int, float, date)
   - Conversion automatique lorsque possible
   - Rejet des données non convertibles

2. **Validation des contraintes** :
   - Valeurs numériques >= 0 (calories, poids, etc.)
   - Formats d'email valides
   - Dates dans un format cohérent
   - Longueurs de chaînes respectées

3. **Validation de complétude** :
   - Champs obligatoires présents
   - Gestion des valeurs nulles selon les règles métier

### 5.2. Nettoyage des Données

1. **Suppression des doublons** :
   - Basée sur des clés uniques (nom, email, etc.)
   - Conservation de la première occurrence

2. **Normalisation** :
   - Normalisation des chaînes (minuscules, suppression espaces)
   - Normalisation des valeurs énumérées (type, niveau, etc.)
   - Conversion des unités (standardisation)

3. **Gestion des valeurs manquantes** :
   - Remplacement par valeurs par défaut (0 pour numériques)
   - Conservation des NULL pour champs optionnels
   - Logging des valeurs manquantes pour analyse

### 5.3. Gestion des Erreurs

1. **Logging** :
   - Logging de toutes les erreurs avec contexte
   - Niveaux de log (INFO, WARNING, ERROR)
   - Traçabilité complète des opérations

2. **Récupération** :
   - Gestion des erreurs par source (une source en échec n'empêche pas les autres)
   - Rollback en cas d'erreur critique
   - Notification des échecs

---

## 6. Métriques de Qualité

### 6.1. Indicateurs Suivis

- **Taux de réussite d'ingestion** : % de données ingérées avec succès
- **Taux de doublons détectés** : % de doublons identifiés et supprimés
- **Taux de valeurs manquantes** : % de valeurs manquantes par champ
- **Taux d'erreurs de validation** : % de données rejetées pour non-conformité
- **Temps d'exécution ETL** : Durée totale du pipeline

### 6.2. Tableau de Bord Qualité

Ces métriques sont disponibles dans l'interface Streamlit (section "Configuration" → "Qualité des données").

---

## 7. Conclusion

Ce rapport d'inventaire recense toutes les sources de données utilisées dans le projet HealthAI Coach, avec leurs caractéristiques, leurs règles de qualité et leur intégration dans le pipeline ETL. Les sources sont variées (API, CSV, données simulées) et sont traitées de manière automatisée et sécurisée pour garantir la qualité et l'exploitabilité des données.

---

**Document généré le** : 2025  
**Dernière mise à jour** : 2025  
**Version** : 1.0

