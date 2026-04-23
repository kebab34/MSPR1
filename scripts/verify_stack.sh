#!/usr/bin/env bash
# Vérifie que Supabase local + ports attendus par MSPR sont accessibles.
set -euo pipefail
RED='\033[0;31m'; GRN='\033[0;32m'; N='\033[0m'
ok() { echo -e "${GRN}OK${N} $*"; }
bad() { echo -e "${RED}KO${N} $*"; }
echo "== Supabase =="
if command -v supabase &>/dev/null; then
  if supabase status &>/dev/null; then
    ok "supabase local tourne (supabase status)"
  else
    bad "supabase ne répond pas — lance : supabase start"
    exit 1
  fi
else
  bad "supabase CLI absent"
  exit 1
fi
echo "== Ports hôte =="
for p in 54321 54322; do
  if ss -tlnp 2>/dev/null | grep -q ":${p} "; then
    ok "port ${p} (écoute)"
  else
    bad "port ${p} (rien n’écoute) — vérifier supabase start"
  fi
done
echo "== API Supabase (Kong) =="
code=$(curl -sS -o /dev/null -m 3 -w '%{http_code}' "http://127.0.0.1:54321/rest/v1/" || echo "0")
if [[ "$code" == "2"* ]] || [[ "$code" == "401" ]] || [[ "$code" == "404" ]]; then
  ok "http://127.0.0.1:54321 (REST répond, code HTTP $code)"
else
  bad "http://127.0.0.1:54321 (code $code) — l’URL projet doit utiliser le port 54321, pas 54323 (Studio seul)"
fi
if command -v psql &>/dev/null; then
  if psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" -c "select 1" &>/dev/null; then
    ok "PostgreSQL 127.0.0.1:54322 (connexion directe)"
  else
    bad "PostgreSQL 54322 (psql a échoué)"
  fi
else
  echo " (psql absent, test PG sauté)"
fi
echo "== Docker (optionnel) =="
if docker info &>/dev/null; then
  if docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^mspr_api$'; then
    if docker exec mspr_api getent hosts host.docker.internal &>/dev/null; then
      ok "mspr_api: host.docker.internal résolu (compose OK)"
    else
      bad "mspr_api: host.docker.internal"
    fi
  else
    echo "  (conteneur mspr_api non démarré — ex. docker compose up -d)"
  fi
else
  echo "  (docker indisponible, ignoré)"
fi
echo "Terminé."
