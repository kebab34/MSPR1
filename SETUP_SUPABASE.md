# 🔧 Guide de configuration Supabase

## Étape 1 : Créer un compte Supabase

1. Aller sur https://supabase.com
2. Cliquer sur "Start your project"
3. Se connecter avec GitHub (recommandé) ou créer un compte

## Étape 2 : Créer un nouveau projet

1. Cliquer sur "New Project"
2. Remplir les informations :
   - **Name** : MSPR1 (ou le nom de votre choix)
   - **Database Password** : Choisir un mot de passe fort (⚠️ À NOTER, vous en aurez besoin)
   - **Region** : Choisir la région la plus proche (ex: West Europe)
   - **Pricing Plan** : Free tier (suffisant pour commencer)

3. Cliquer sur "Create new project"
4. ⏳ Attendre 2-3 minutes que le projet soit créé

## Étape 3 : Récupérer les credentials

Une fois le projet créé :

### 3.1 URL du projet
- Dans le dashboard Supabase, l'URL est visible en haut
- Format : `https://xxxxx.supabase.co`
- **Copier cette URL**

### 3.2 Clé API (Anon Key)
1. Aller dans **Settings** (icône engrenage en bas à gauche)
2. Cliquer sur **API**
3. Dans la section **Project API keys**
4. Copier la clé **anon public** (c'est la `SUPABASE_KEY`)

### 3.3 Clé Service Role
1. Toujours dans **Settings > API**
2. Dans la section **Project API keys**
3. Copier la clé **service_role** (⚠️ SECRÈTE, ne jamais l'exposer publiquement)
4. C'est la `SUPABASE_SERVICE_KEY`

### 3.4 URL de connexion PostgreSQL
1. Aller dans **Settings > Database**
2. Dans la section **Connection string**
3. Choisir **URI** (pas Transaction)
4. Copier l'URL (format : `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`)
5. ⚠️ Remplacer `[YOUR-PASSWORD]` par le mot de passe que vous avez défini à l'étape 2

## Étape 4 : Configurer le fichier .env

Ouvrir le fichier `.env` dans le projet et remplacer :

```env
SUPABASE_URL=https://xxxxx.supabase.co          # Votre URL Supabase
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Votre anon key
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Votre service_role key
DATABASE_URL=postgresql://postgres:VOTRE_MOT_DE_PASSE@db.xxxxx.supabase.co:5432/postgres
```

## Étape 5 : Vérifier la connexion

Une fois configuré, vous pouvez tester avec :

```bash
docker-compose up api
```

Et vérifier que l'API démarre sans erreur de connexion.

## 📝 Notes importantes

- ⚠️ **Ne jamais commiter le fichier `.env`** (déjà dans .gitignore)
- 🔒 **Garder les clés secrètes** (surtout la service_role)
- 📊 Le projet Supabase gratuit inclut :
  - 500 MB de base de données
  - 2 GB de bande passante
  - 50 000 utilisateurs actifs par mois

## 🆘 En cas de problème

- Vérifier que l'URL Supabase est correcte
- Vérifier que les clés API sont bien copiées (sans espaces)
- Vérifier que le mot de passe dans DATABASE_URL est correct
- Vérifier que le projet Supabase est bien actif

