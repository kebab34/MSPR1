# 🔧 Configuration Supabase Local

## Utilisation de Supabase en local

Si tu utilises Supabase en local (via Supabase CLI), voici comment configurer le projet.

## 1. Obtenir les clés API de Supabase local

### Via le Dashboard local

1. **Ouvrir le dashboard Supabase local** : http://localhost:54323
2. **Aller dans Settings** (icône engrenage en bas à gauche)
3. **Cliquer sur API**
4. **Copier les clés suivantes** :
   - **anon public** : C'est la `SUPABASE_KEY`
   - **service_role** : C'est la `SUPABASE_SERVICE_KEY` (⚠️ SECRÈTE)

### Via la ligne de commande

Si tu utilises Supabase CLI, tu peux aussi obtenir les clés avec :

```bash
supabase status
```

Cela affichera toutes les informations de connexion, y compris les clés API.

## 2. Obtenir l'URL de connexion PostgreSQL

Pour la `DATABASE_URL`, utilise :

```bash
supabase status
```

Ou directement dans le dashboard local :
- **Settings > Database > Connection string**
- Format : `postgresql://postgres:postgres@localhost:54322/postgres`

⚠️ **Note** : Le port PostgreSQL est généralement **54322** (pas 54323)

## 3. Mettre à jour le fichier .env

Édite ton fichier `.env` à la racine du projet :

```env
# Supabase Local
SUPABASE_URL=http://localhost:54323
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # anon public key
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # service_role key

# Database (port PostgreSQL local, généralement 54322)
DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres

# JWT Secret (peut être n'importe quelle chaîne pour le local)
JWT_SECRET=your-local-jwt-secret-key

# ETL Schedule
ETL_SCHEDULE=0 */6 * * *

# API URL (pour Streamlit)
API_URL=http://localhost:8000
```

## 4. Redémarrer les services

Après avoir mis à jour le `.env`, redémarre les services :

```bash
# Arrêter les services
pkill -f 'uvicorn|next'

# Redémarrer l'API
cd api && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Redémarrer Streamlit
cd web && npm run dev &
```

## 5. Vérifier la connexion

Teste la connexion à Supabase local :

```bash
curl http://localhost:54323/rest/v1/
```

Si tu obtiens une réponse, c'est que Supabase local fonctionne correctement.

## Ports par défaut Supabase local

- **Dashboard/API** : `http://localhost:54321` (ou `54323` selon ta config)
- **PostgreSQL** : `localhost:54322`
- **Studio** : `http://localhost:54323` (dashboard web)

## Dépannage

### Problème : "Connection refused"

- Vérifie que Supabase local est bien démarré : `supabase status`
- Vérifie que le port est correct (54323 dans ton cas)

### Problème : "Invalid API key"

- Vérifie que tu as bien copié la clé complète (elles sont très longues)
- Assure-toi d'utiliser la bonne clé (anon pour SUPABASE_KEY, service_role pour SUPABASE_SERVICE_KEY)

### Problème : "Database connection failed"

- Vérifie que PostgreSQL est bien démarré
- Vérifie le port PostgreSQL (généralement 54322)
- Vérifie le mot de passe (par défaut: `postgres`)
