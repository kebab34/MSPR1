# 🔑 Comment trouver la Service Key de Supabase Local

## Méthode 1 : Via le Dashboard Supabase Local (Recommandé)

1. **Ouvre le dashboard** : http://localhost:54323
2. **Va dans Settings** (icône engrenage ⚙️ en bas à gauche)
3. **Clique sur "API"** dans le menu de gauche
4. **Cherche la section "Project API keys"**
5. **La service_role key peut être masquée** :
   - Cherche un bouton "Reveal", "Show", "👁️" ou "🔓"
   - Clique dessus pour afficher la clé complète
   - Elle commence généralement par `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## Méthode 2 : Via Supabase CLI

Si tu as Supabase CLI installé :

```bash
supabase status
```

Cette commande affiche toutes les informations de connexion, y compris :
- `API URL`
- `anon key`
- `service_role key`

## Méthode 3 : Dans les fichiers de configuration

La clé peut être stockée dans les fichiers de config Supabase :

```bash
# Cherche dans le dossier home
cat ~/.supabase/config.toml

# Ou dans le projet
cat .supabase/config.toml

# Ou dans le dossier de Supabase
find ~ -name "config.toml" -path "*supabase*" 2>/dev/null
```

## Méthode 4 : Via les variables d'environnement

Si Supabase est lancé via Docker ou un script, vérifie les variables d'environnement :

```bash
# Si lancé avec Docker
docker ps | grep supabase
docker exec <container_id> env | grep SERVICE

# Si lancé avec un script
cat ~/.bashrc | grep SUPABASE
cat ~/.zshrc | grep SUPABASE
```

## Méthode 5 : Générer une nouvelle clé (si nécessaire)

Si tu ne trouves vraiment pas la clé, tu peux la régénérer dans le dashboard :

1. Va dans **Settings > API**
2. Cherche l'option "Reset" ou "Regenerate" pour la service_role key
3. ⚠️ **Attention** : Cela invalidera l'ancienne clé

## Astuce : Utiliser temporairement l'anon key

Pour tester rapidement, tu peux temporairement utiliser l'anon key comme service key dans ton `.env` :

```env
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # anon key
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # même clé temporairement
```

⚠️ **Note** : Ce n'est pas recommandé pour la production, mais ça fonctionne pour le développement local.

## Vérifier que la clé fonctionne

Une fois que tu as la clé, teste-la :

```bash
# Test avec curl
curl -H "apikey: TON_SERVICE_KEY" \
     -H "Authorization: Bearer TON_SERVICE_KEY" \
     http://localhost:54323/rest/v1/
```

Si tu obtiens une réponse (même une erreur), c'est que la clé est valide.

## Structure de la clé

Les clés JWT Supabase ont cette structure :
- **Début** : `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9`
- **Longueur** : Très longue (plusieurs centaines de caractères)
- **Format** : Base64 encodé

Si ta clé est trop courte, c'est qu'elle est tronquée ou incorrecte.
