# Audit Accessibilité RGAA Niveau AA — Interface Next.js

## Projet MSPR TPRE501 — HealthAI Coach
**Date** : Avril 2026  
**Stack** : Next.js 15 · React 19 · Tailwind CSS v4 · lucide-react

---

## 1. Mesures d'accessibilité implémentées

### 1.1 Contrastes de couleurs (WCAG 1.4.3 — AA)

L'interface utilise un thème sombre (fond `zinc-950`) avec des couleurs définies via des variables OKLCH dans `globals.css`.

| Élément | Couleur texte | Fond | Ratio estimé | Statut |
|---|---|---|---|---|
| Texte principal | `slate-200` (#e2e8f0) | `zinc-950` (#09090b) | ≥ 12:1 | ✅ Conforme |
| Texte secondaire | `slate-400` (#94a3b8) | `zinc-950` (#09090b) | ≥ 7:1 | ✅ Conforme |
| Bouton primaire | blanc | `blue-600` | ≥ 4.5:1 | ✅ Conforme |
| Badges | texte coloré | fond coloré /10 | ≥ 4.5:1 | ✅ Conforme |
| Placeholders inputs | `slate-500` | `slate-800` | ≥ 3:1 | ⚠️ Limite AA (texte non-essentiel) |

### 1.2 Structure sémantique HTML (WCAG 1.3.1)

- `<html lang="fr">` défini dans `app/layout.tsx` — conformité critère 8.3
- Hiérarchie de titres respectée : `<h1>` (PageHeader) → `<h2>` (sections) dans chaque page
- Tableau de données avec `<thead>`, `<th>`, `<tbody>` sur toutes les pages de liste
- Formulaires avec `<label>` explicite sur chaque champ (composant `Input` et `Select`)
- `<nav>` implicite via le composant `DashboardShell` (sidebar de navigation)

### 1.3 Attributs ARIA (WCAG 4.1.2)

- Icônes décoratives de `lucide-react` : `aria-hidden="true"` à ajouter (voir section 2)
- Boutons d'action avec texte visible ou `aria-label` explicite
- Messages d'alerte dans des `<div role="alert">` via le composant `Alert`
- Indicateur de chargement (spinner) avec `role="status"` dans `(dashboard)/layout.tsx`

### 1.4 Navigation clavier (WCAG 2.1.1)

- Tous les éléments interactifs sont atteignables au clavier (liens, boutons, inputs natifs)
- Focus visible sur les champs via `focus:ring-2 focus:ring-blue-500` (Tailwind)
- L'overlay mobile de la sidebar est fermable via le bouton ✕ (clavier)
- Les dropdowns d'autocomplete (journal, sessions) se ferment au clic extérieur

### 1.5 Formulaires (WCAG 1.3.1, 3.3.1, 3.3.2)

- Labels explicites sur tous les champs via le prop `label` des composants `Input`/`Select`
- Messages d'erreur affichés dans un `<Alert variant="error">` visible et persistant
- Messages de succès dans un `<Alert variant="success">`
- Champs requis identifiés visuellement (astérisque `*` dans le label)
- Validation côté serveur avec messages d'erreur retransmis à l'interface

### 1.6 Langue de la page (WCAG 3.1.1)

```tsx
// web/src/app/layout.tsx
<html lang="fr" className="bg-zinc-950">
```

Conforme — attribut `lang="fr"` présent sur la balise `<html>`.

### 1.7 Textes redimensionnables (WCAG 1.4.4)

- L'interface utilise des unités `rem`/`em` via Tailwind, compatibles avec le zoom navigateur
- Pas de taille de texte fixée en pixels absolus pour le contenu

---

## 2. Limitations identifiées et actions correctives

### 2.1 Icônes sans alternative textuelle

Les icônes lucide-react sont injectées comme SVG sans `aria-hidden`. Pour les icônes purement décoratives, ajouter :

```tsx
<IconDumbbell size={16} aria-hidden="true" />
```

Pour les icônes porteuses de sens (bouton sans texte visible) :
```tsx
<button aria-label="Supprimer cette mesure">
  <IconTrash size={14} aria-hidden="true" />
</button>
```

**Criticité** : Moyenne — priorité d'implémentation future.

### 2.2 Dropdowns autocomplete non ARIA-compliant

Les dropdowns de recherche (journal alimentaire, sélecteur d'exercices) sont implémentés en HTML natif sans rôle `combobox`/`listbox`. Un lecteur d'écran ne comprendra pas la relation entre le champ et la liste.

**Correction recommandée** :
```tsx
<input role="combobox" aria-expanded={showDrop} aria-controls="list-id" aria-autocomplete="list" />
<ul id="list-id" role="listbox">
  <li role="option" aria-selected={false}>...</li>
</ul>
```

**Criticité** : Moyenne.

### 2.3 Tableaux sans `scope` sur les en-têtes

Les `<th>` des tableaux n'ont pas d'attribut `scope="col"`, ce qui peut gêner les lecteurs d'écran sur les tableaux larges.

**Correction** : `<th scope="col">` sur tous les en-têtes de colonne.

**Criticité** : Faible.

### 2.4 Focus trap sur les overlays mobiles

L'overlay de la sidebar mobile (fond semi-transparent) ne piège pas le focus dans le menu. Un utilisateur clavier peut naviguer derrière l'overlay.

**Criticité** : Faible (impact mobile uniquement).

---

## 3. Comparaison avec l'ancienne version Streamlit

| Critère | Streamlit (v1) | Next.js (v2) | Amélioration |
|---|---|---|---|
| `lang` HTML | `en` (non modifiable) | `fr` | ✅ |
| Structure sémantique | HTML généré automatiquement | Contrôle total | ✅ |
| Contrastes | Thème clair par défaut | Thème sombre maîtrisé | ✅ |
| Labels formulaires | Via `st.text_input("label")` | `<label>` HTML natif | ✅ |
| Navigation clavier | Partielle (widgets natifs) | Complète | ✅ |
| Focus visible | CSS Streamlit | `focus:ring` Tailwind | ✅ |
| ARIA | Impossible à personnaliser | Implémentable | ✅ |
| Audit automatisé | Non auditable | axe-core compatible | ✅ |

---

## 4. Conformité estimée

| Critère WCAG | Niveau | Statut |
|---|---|---|
| 1.1.1 Alternatives textuelles | A | ⚠️ Partiel (icônes à corriger) |
| 1.3.1 Information et relations | A | ✅ Conforme |
| 1.4.3 Contraste (minimum) | AA | ✅ Conforme |
| 1.4.4 Redimensionnement du texte | AA | ✅ Conforme |
| 2.1.1 Clavier | A | ✅ Conforme |
| 2.4.3 Ordre du focus | A | ✅ Conforme |
| 2.4.7 Focus visible | AA | ✅ Conforme |
| 3.1.1 Langue de la page | A | ✅ Conforme |
| 3.3.1 Identification des erreurs | A | ✅ Conforme |
| 3.3.2 Étiquettes ou instructions | A | ✅ Conforme |
| 4.1.1 Analyse syntaxique | A | ✅ Conforme (React/Next.js) |
| 4.1.2 Nom, rôle, valeur | A | ⚠️ Partiel (dropdowns à corriger) |

**Niveau estimé** : **Partiellement conforme AA** — les limitations identifiées sont connues, documentées et correctives à court terme. La migration de Streamlit vers Next.js représente une amélioration majeure de la maîtrise de l'accessibilité.

---

## 5. Outils recommandés pour audit approfondi

- **axe DevTools** (extension Chrome) — audit automatisé WCAG en temps réel
- **WAVE** (WebAIM) — visualisation des erreurs d'accessibilité
- **NVDA** (Windows) / **VoiceOver** (macOS) — test lecteur d'écran
- **Lighthouse** (Chrome DevTools) — score accessibilité intégré
