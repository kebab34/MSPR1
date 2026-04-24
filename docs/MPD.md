# Modèle Physique de Données (MPD)

## Projet MSPR TPRE501 — HealthAI Coach

**SGBD** : PostgreSQL 15 (Supabase)  
**Date** : Avril 2026

---

## Schéma des tables

```
┌─────────────────────────────────────────┐
│              UTILISATEURS               │
├─────────────────────────────────────────┤
│ PK  id_utilisateur  UUID  NOT NULL      │
│     email           TEXT  UNIQUE NN     │
│     nom             TEXT                │
│     prenom          TEXT                │
│     age             INTEGER  (>0,<150)  │
│     sexe            TEXT  (M/F/Autre)   │
│     poids           DECIMAL(5,2)  (>0)  │
│     taille          DECIMAL(5,2)  (>0)  │
│     objectifs       TEXT[]  DEFAULT {}  │
│     type_abonnement TEXT  DEFAULT freemium │
│     app_role        TEXT  DEFAULT user  │
│     auth_id         UUID  (Supabase auth) │
│     created_at      TIMESTAMPTZ         │
│     updated_at      TIMESTAMPTZ         │
└────────────────┬────────────────────────┘
                 │ 1
     ┌───────────┼───────────────────────────────────────────────┐
     │           │                                               │
     │ N         │ N                    N                        │ N
┌────┴──────────────┐  ┌───────────────────┐  ┌────────────────────────────┐  ┌──────────────────────────┐
│  JOURNAL_          │  │  SESSIONS_SPORT   │  │  MESURES_BIOMETRIQUES      │  │  OBJECTIFS               │
│  ALIMENTAIRE       │  ├───────────────────┤  ├────────────────────────────┤  ├──────────────────────────┤
├────────────────────┤  │ PK id_session UUID│  │ PK id_mesure  UUID         │  │ PK id_objectif  UUID     │
│ PK id_journal UUID │  │    date_session   │  │    date_mesure TIMESTAMPTZ │  │    type_objectif TEXT NN │
│    date_consomm.   │  │    duree  INTEGER │  │    poids       DECIMAL(5,2)│  │    description   TEXT    │
│    quantite DECIM. │  │    intensite TEXT │  │    freq_card.  INTEGER     │  │ FK id_utilisateur UUID   │
│ FK id_utilisateur  │  │ FK id_utilisateur │  │    sommeil     DECIMAL(4,2)│  │    created_at            │
│ FK id_aliment      │  │    created_at     │  │    calories_br DECIMAL     │  │    updated_at            │
│    created_at      │  │    updated_at     │  │ FK id_utilisateur UUID     │  └──────────────────────────┘
│    updated_at      │  └────────┬──────────┘  │    created_at              │
└────────┬───────────┘           │ 1           │    updated_at              │
         │ N                     │ N           └────────────────────────────┘
         │                ┌──────┴──────────────────┐
         │                │   SESSION_EXERCICES      │  ← table associative
         │                ├──────────────────────────┤
         │                │ PK,FK id_session  UUID   │
         │                │ PK,FK id_exercice UUID   │
         │                │    nombre_series INTEGER │
         │                │    nombre_reps   INTEGER │
         │                │    poids  DECIMAL(5,2)   │
         │                │    duree  INTEGER (sec)  │
         │                └──────────┬───────────────┘
         │                           │ N
┌────────┴───────────────────────────┴──────────────────────────┐
│                            ALIMENTS                            │
├────────────────────────────────────────────────────────────────┤
│ PK  id_aliment    UUID   NOT NULL                              │
│     nom           TEXT   UNIQUE NOT NULL                       │
│     calories      DECIMAL(10,2)  DEFAULT 0                     │
│     proteines     DECIMAL(10,2)  DEFAULT 0                     │
│     glucides      DECIMAL(10,2)  DEFAULT 0                     │
│     lipides       DECIMAL(10,2)  DEFAULT 0                     │
│     fibres        DECIMAL(10,2)  DEFAULT 0                     │
│     unite         TEXT   DEFAULT '100g'                        │
│     source        TEXT                                         │
│     created_at    TIMESTAMPTZ                                  │
│     updated_at    TIMESTAMPTZ                                  │
└────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                             EXERCICES                                │
├──────────────────────────────────────────────────────────────────────┤
│ PK  id_exercice      UUID   NOT NULL                                 │
│     nom              TEXT   UNIQUE NOT NULL                          │
│     type             TEXT   (force/cardio/flexibilite/autre)         │
│     groupe_musculaire TEXT                                           │
│     niveau           TEXT   DEFAULT 'debutant'                       │
│     equipement       TEXT                                            │
│     description      TEXT                                            │
│     instructions     TEXT                                            │
│     source           TEXT                                            │
│     created_at       TIMESTAMPTZ                                     │
│     updated_at       TIMESTAMPTZ                                     │
└──────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                   RECETTES                             │
├────────────────────────────────────────────────────────┤
│ PK  id_recette         UUID   NOT NULL                 │
│     nom                TEXT   NOT NULL                 │
│     description        TEXT                            │
│     temps_preparation  INTEGER  (>=0)                  │
│     nombre_personnes   INTEGER  DEFAULT 1              │
│     difficulte         TEXT  (facile/moyen/difficile)  │
│     created_at         TIMESTAMPTZ                     │
│     updated_at         TIMESTAMPTZ                     │
└──────────────┬─────────────────────────────────────────┘
               │ 1
               │ N
┌──────────────┴──────────────────────────┐
│         RECETTE_ALIMENTS                │  ← table associative
├─────────────────────────────────────────┤
│ PK,FK id_recette  UUID                  │
│ PK,FK id_aliment  UUID                  │
│        quantite   DECIMAL(10,2)  (>0)   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       PROGRESSIONS                          │
├─────────────────────────────────────────────────────────────┤
│ PK  id_progression  UUID   NOT NULL                         │
│ FK  id_utilisateur  UUID                                    │
│ FK  id_exercice     UUID                                    │
│     date_progression TIMESTAMPTZ                            │
│     valeur_avant     DECIMAL(10,2)                          │
│     valeur_apres     DECIMAL(10,2)                          │
│     type_progression TEXT  (poids/repetitions/duree)        │
│     created_at       TIMESTAMPTZ                            │
│     updated_at       TIMESTAMPTZ                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Relations

| Table source | Clé étrangère | Table cible | Cardinalité | ON DELETE |
|---|---|---|---|---|
| journal_alimentaire | id_utilisateur | utilisateurs | N → 1 | CASCADE |
| journal_alimentaire | id_aliment | aliments | N → 1 | CASCADE |
| sessions_sport | id_utilisateur | utilisateurs | N → 1 | CASCADE |
| session_exercices | id_session | sessions_sport | N → 1 | CASCADE |
| session_exercices | id_exercice | exercices | N → 1 | CASCADE |
| mesures_biometriques | id_utilisateur | utilisateurs | N → 1 | CASCADE |
| objectifs | id_utilisateur | utilisateurs | N → 1 | CASCADE |
| progressions | id_utilisateur | utilisateurs | N → 1 | CASCADE |
| progressions | id_exercice | exercices | N → 1 | CASCADE |
| recette_aliments | id_recette | recettes | N → 1 | CASCADE |
| recette_aliments | id_aliment | aliments | N → 1 | CASCADE |

---

## Index

| Table | Colonne(s) | Type |
|---|---|---|
| utilisateurs | email | UNIQUE |
| utilisateurs | type_abonnement | B-tree |
| utilisateurs | created_at DESC | B-tree |
| aliments | nom | UNIQUE |
| aliments | calories | B-tree |
| exercices | nom | UNIQUE |
| exercices | type, niveau | B-tree |
| journal_alimentaire | id_utilisateur | B-tree |
| journal_alimentaire | date_consommation DESC | B-tree |
| sessions_sport | id_utilisateur | B-tree |
| sessions_sport | date_session DESC | B-tree |
| mesures_biometriques | id_utilisateur | B-tree |
| mesures_biometriques | date_mesure DESC | B-tree |

---

## Contraintes notables

- Tous les UUID sont générés côté base avec `gen_random_uuid()`
- `updated_at` mis à jour automatiquement via trigger `update_updated_at_column()`
- Les suppressions en cascade garantissent l'intégrité référentielle : supprimer un utilisateur supprime toutes ses données associées
- `type_abonnement` : `freemium | premium | premium+ | B2B`
- `intensite` session : `faible | moderee | elevee`
- `niveau` exercice : `debutant | intermediaire | avance`
- `sexe` utilisateur : `M | F | Autre`
