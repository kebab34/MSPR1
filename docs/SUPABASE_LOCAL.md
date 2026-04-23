# Configuration Supabase local

## Les trois ports utiles (ne pas les confondre)

| Rôle | Port | URL d’exemple |
|------|------|---------------|
| **API (Kong) — `SUPABASE_URL` pour l’appli** | **54321** | `http://127.0.0.1:54321` (REST, Auth, etc.) |
| **PostgreSQL direct — `DATABASE_URL`** | **54322** | `postgresql://postgres:postgres@127.0.0.1:54322/postgres` |
| **Studio (interface web, debug)** | **54323** | `http://127.0.0.1:54323` — *ce n’est pas* l’URL d’API pour le code. |

L’ancienne version de ce document indiquait par erreur `54323` pour `SUPABASE_URL` : c’est la cause classique d’**API injoignable** alors que le Studio s’ouvre.

## 1. Clés API

- Studio : `http://127.0.0.1:54323` → **Settings → API** (anon, service_role)
- CLI : `supabase status` (même information)

## 2. Fichier `.env` (API / ETL lancés **hors** Docker, depuis ta machine)

```env
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_KEY=...   # anon
SUPABASE_SERVICE_KEY=...  # service_role
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
JWT_SECRET=...     # idem à la section JWT du `supabase status` / `config.toml` (sinon 401 côté API)
```

## 3. Avec **Docker Compose** (services `mspr_api`, `mspr_etl`, etc.)

L’hôte n’est plus `127.0.0.1` *vu depuis le conteneur*. Le `docker-compose.yml` du dépôt force :

- `SUPABASE_URL=http://host.docker.internal:54321`
- `DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:54322/postgres`
- + `extra_hosts: host.docker.internal:host-gateway`

Tes clés viennent toujours du **`.env` à la racine** (substitution `${SUPABASE_KEY}`…), mais **l’adresse d’hôte** est gérée par Compose. Ne mets **pas** `127.0.0.1` pour Supabase/Postgres si ton code tourne *dans* le conteneur (sauf si tu as une config réseau spécifique).

**Prérequis** : Supabase local doit tourner *sur l’hôte* : `supabase start`. Sinon les ports 54321/54322 ne répondent pas.

## 4. Vérification rapide

```bash
chmod +x scripts/verify_stack.sh
./scripts/verify_stack.sh
```

Test manuel API :

```bash
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:54321/rest/v1/
# Souvent 401 ou 200 selon le endpoint — l’essentiel est qu’on ne soit pas "connection refused"
```

## 5. Dépannage

- **Connection refused (54321 / 54322)** : `supabase start` et `supabase status`.
- **Injoignable depuis le conteneur** : vérifier `host.docker.internal` (pare-feu, `sudo ufw allow from 172.16.0.0/12` côté Docker, etc.).
- **Invalid API key** : clés incomplètes ou mauvais fichier `.env` (anon vs `service_role`).
- **Auth / token** : `JWT_SECRET` identique à celui utilisé par Supabase local.
- **Cloud Supabase** : `SUPABASE_URL` = `https://xxxxx.supabase.co`, `DATABASE_URL` = chaîne *Database* du dashboard (hôte `db.xxxxx.supabase.co`, pas `127.0.0.1`).
