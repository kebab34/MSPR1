# 📊 Étape 3 : Création de la Base de Données

## Objectif

Créer les tables nécessaires dans Supabase selon les besoins du projet MSPR.

---

## 🎯 Étapes à suivre

### 1. Analyser le sujet MSPR

1. **Lire le sujet PDF** dans `Sujet/`
2. **Identifier** :
   - Les entités métier (ex: Utilisateurs, Commandes, Produits, etc.)
   - Les relations entre entités
   - Les données à stocker
   - Les contraintes (unicité, valeurs par défaut, etc.)

### 2. Créer le MCD (Modèle Conceptuel de Données)

Dessinez ou documentez les entités et leurs relations :

```
Exemple :
[Utilisateur] --< crée >-- [Commande]
[Commande] --< contient >-- [LigneCommande]
[LigneCommande] --< référence >-- [Produit]
```

### 3. Créer le MLD (Modèle Logique de Données)

Définissez les tables avec leurs colonnes :

| Table | Colonnes | Type | Contraintes |
|-------|----------|------|-------------|
| users | id | UUID | PK |
| users | email | TEXT | UNIQUE, NOT NULL |
| users | name | TEXT | |
| users | created_at | TIMESTAMP | DEFAULT NOW() |

### 4. Créer les tables dans Supabase

#### Via SQL Editor (Recommandé pour les structures complexes)

1. **Ouvrir SQL Editor**
   - Cliquer sur **"SQL Editor"** dans la barre latérale

2. **Créer un nouveau script**
   - Cliquer sur **"New Query"**

3. **Copier le SQL**
   - Utiliser le fichier `docs/create_tables_example.sql` comme base
   - Adapter selon vos besoins

4. **Exécuter**
   - Cliquer sur **"Run"** ou `Ctrl+Enter`

### 5. Créer les relations (Foreign Keys)

1. **Dans Table Editor**
   - Ouvrir la table qui doit référencer une autre table
   - Ajouter une colonne (ex: `user_id`)
   - Type : `uuid` (ou le type de la clé primaire référencée)
   - Cliquer sur **"Add Foreign Key"**
   - Sélectionner la table et colonne référencées

2. **Via SQL**
   ```sql
   ALTER TABLE orders 
   ADD CONSTRAINT fk_orders_user 
   FOREIGN KEY (user_id) 
   REFERENCES users(id) 
   ON DELETE CASCADE;
   ```

### 6. Créer les index (pour améliorer les performances)

Dans SQL Editor :

```sql
-- Index sur une colonne fréquemment utilisée
CREATE INDEX idx_users_email ON users(email);

-- Index composite
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);
```

### 7. Configurer RLS (Row Level Security) - Optionnel

Si vous voulez sécuriser l'accès aux données :

```sql
-- Activer RLS sur une table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Créer une politique
CREATE POLICY "Users can read own data"
  ON users FOR SELECT
  USING (auth.uid() = id);
```

---

## 📝 Checklist

- [ ] Sujet MSPR analysé
- [ ] MCD créé (entités et relations)
- [ ] MLD créé (tables et colonnes)
- [ ] Tables créées dans Supabase
- [ ] Relations (foreign keys) définies
- [ ] Index créés sur les colonnes importantes
- [ ] RLS configuré (si nécessaire)
- [ ] Données de test insérées (optionnel)

---

## 🔍 Vérification

Après avoir créé vos tables, testez :

1. **Vérifier les tables**
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public'
   ORDER BY table_name;
   ```

2. **Vérifier les colonnes**
   ```sql
   SELECT column_name, data_type, is_nullable
   FROM information_schema.columns
   WHERE table_name = 'votre_table'
   ORDER BY ordinal_position;
   ```

3. **Tester une insertion**
   ```sql
   INSERT INTO users (email, name) 
   VALUES ('test@example.com', 'Test User');
   ```

4. **Tester une sélection**
   ```sql
   SELECT * FROM users;
   ```

---

## 📚 Ressources

- Documentation Supabase : https://supabase.com/docs/guides/database
- Guide SQL : https://supabase.com/docs/guides/database/tables
- RLS : https://supabase.com/docs/guides/auth/row-level-security

---

