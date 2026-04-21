# Audit Accessibilite RGAA Niveau AA - Interface Streamlit

## Projet MSPR TPRE501 - HealthAI Coach
**Date** : Mars 2026

---

## 1. Mesures d'accessibilite implementees

### 1.1. Contrastes de couleurs
- Les textes descriptifs utilisent `#4b5563` sur fond blanc (ratio >= 4.6:1, conforme AA)
- Les titres principaux utilisent `#1a1a2e` sur fond blanc (ratio >= 15:1)
- La banniere hero utilise du blanc sur fond degrade colore (ratio >= 4.5:1)

### 1.2. Structure semantique HTML
- Balise `<header>` avec `role="banner"` pour la section hero
- Titres hierarchiques (`<h1>`, `<h2>`) utilises via le HTML custom
- Attributs `role="status"` sur les cartes de statistiques
- Attributs `role="heading"` avec `aria-level` pour les titres de section

### 1.3. Attributs ARIA
- `aria-label` sur les cartes de statistiques pour les lecteurs d'ecran
- `aria-hidden="true"` sur les icones decoratives (emojis)
- `aria-label` sur la banniere principale

### 1.4. Navigation clavier
- Lien "skip to content" (`skip-link`) visible au focus pour acceder directement au contenu
- Styles de focus visibles (`outline: 3px solid`) sur tous les elements interactifs
- Navigation par tabulation fonctionnelle sur les formulaires Streamlit natifs

### 1.5. Formulaires
- Labels explicites sur tous les champs de formulaire (via `st.text_input("Label")`)
- Messages d'erreur affiches via `st.error()` (accessibles)
- Boutons avec texte descriptif

---

## 2. Limitations identifiees (liees a Streamlit)

### 2.1. Limitations natives de Streamlit
Streamlit genere son propre HTML/CSS/JS, ce qui limite le controle sur :

| Critere RGAA | Limitation | Severite |
|--------------|-----------|----------|
| 1.1 Images | Pas de controle sur les `alt` des images generees par Streamlit (graphiques Plotly) | Moyenne |
| 4.1 Multimedia | Les graphiques interactifs n'ont pas de description textuelle alternative native | Moyenne |
| 7.1 Scripts | Les widgets Streamlit utilisent du JS proprietaire non auditable | Faible |
| 8.2 Langue | L'attribut `lang` du `<html>` est fixe par Streamlit (en) | Faible |
| 10.7 Responsive | Le layout responsive est gere par Streamlit (generalement correct) | Faible |
| 12.1 Navigation | La sidebar Streamlit n'est pas un `<nav>` natif | Faible |

### 2.2. Points d'amelioration futurs
- Migration vers une interface React/Next.js pour un controle total de l'accessibilite
- Ajout de descriptions textuelles pour chaque graphique (`st.caption()`)
- Tests avec lecteurs d'ecran (NVDA, VoiceOver)
- Audit automatise avec axe-core ou pa11y

---

## 3. Conformite estimee

| Critere | Statut |
|---------|--------|
| Contrastes de couleurs (1.4.3) | Conforme |
| Textes redimensionnables (1.4.4) | Conforme (Streamlit gere) |
| Navigation clavier (2.1.1) | Partiellement conforme |
| Focus visible (2.4.7) | Conforme (CSS custom) |
| Titres et labels (2.4.6) | Conforme |
| Langue de la page (3.1.1) | Non conforme (limitation Streamlit) |
| Parsing (4.1.1) | Non auditable (HTML genere par Streamlit) |

**Niveau estime** : Partiellement conforme AA (limitations inherentes au framework Streamlit).

---

**Recommandation** : Pour une conformite RGAA AA complete, une migration vers un framework frontend standard (React, Vue) serait necessaire afin de controler integralement le HTML genere.
