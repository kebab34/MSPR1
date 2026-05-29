# ============================================================
# ÉTAPE 1 : deps — installe les dépendances Node
# ============================================================
# Image de base : Node.js 20 sur Alpine Linux (très léger)
FROM node:20-alpine AS deps
WORKDIR /app
# Active corepack (gestionnaire de gestionnaires de paquets) et installe pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate
# Copie uniquement les fichiers de dépendances (optimisation cache Docker)
# Si package.json et pnpm-lock.yaml ne changent pas → Docker réutilise cette couche
COPY package.json pnpm-lock.yaml ./
# Installe exactement les versions du lockfile (reproductible, pas de surprise)
RUN pnpm install --frozen-lockfile

# ============================================================
# ÉTAPE 2 : builder — compile l'application Next.js
# ============================================================
FROM node:20-alpine AS builder
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@latest --activate
# Récupère les node_modules installés à l'étape précédente (sans les réinstaller)
COPY --from=deps /app/node_modules ./node_modules
# Copie tout le code source
COPY . .
# Désactive la télémétrie Next.js (n'envoie pas de stats à Vercel)
ENV NEXT_TELEMETRY_DISABLED=1
# Compile l'application : génère le dossier .next/ avec le code optimisé pour la production
RUN pnpm build

# ============================================================
# ÉTAPE 3 : runner — image finale allégée pour la production
# ============================================================
# Repart d'une image propre sans les outils de build (plus légère et plus sécurisée)
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Démarre le serveur Next.js standalone (généré par output: 'standalone' dans next.config.mjs)
CMD ["node", "server.js"]
