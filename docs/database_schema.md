# 📊 Schéma de Base de Données

## Structure des tables

Ce document décrit le schéma de base de données pour le projet MSPR.

### Tables à créer

> ⚠️ **Note** : Adaptez ce schéma selon les besoins

---

## Exemple de structure

### Table `users` (si nécessaire)

```sql
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour améliorer les performances
CREATE INDEX idx_users_email ON users(email);

-- RLS (Row Level Security) - à activer selon vos besoins
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Politique pour permettre la lecture à tous les utilisateurs authentifiés
CREATE POLICY "Users can read own data"
  ON users FOR SELECT
  USING (auth.uid() = id);
```

### Table `example` (à remplacer par vos tables)

```sql
CREATE TABLE example (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index
CREATE INDEX idx_example_status ON example(status);
CREATE INDEX idx_example_created_at ON example(created_at DESC);
```

---

## Instructions pour créer les tables dans Supabase

1. **Aller dans Supabase Dashboard**
   - Ouvrir votre projet
   - Cliquer sur **Table Editor** dans la barre latérale

2. **Créer une nouvelle table**
   - Cliquer sur **"New Table"**
   - Donner un nom à la table
   - Ajouter les colonnes une par une

3. **Ou utiliser SQL Editor**
   - Aller dans **SQL Editor**
   - Coller le SQL ci-dessus
   - Exécuter la requête

---

## Modèle Conceptuel de Données (MCD)

À compléter selon votre sujet MSPR :

```
[Entité 1] --< [Relation] >-- [Entité 2]
```

---

## Modèle Logique de Données (MLD)

À compléter selon votre sujet MSPR avec :
- Les tables
- Les relations (foreign keys)
- Les contraintes
- Les index

---

## Notes importantes

- **UUID vs Serial** : Utilisez UUID pour les IDs (recommandé par Supabase)
- **Timestamps** : Utilisez `TIMESTAMP WITH TIME ZONE` pour les dates
- **RLS** : Activez Row Level Security pour la sécurité des données
- **Index** : Créez des index sur les colonnes fréquemment utilisées dans les requêtes

