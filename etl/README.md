# ETL (aligné sujet) — Kaggle + exécution

Le pipeline charge **4 sources** (pas de dataset recettes dans le cahier des charges) :

| # | Table(s) cible | Source |
|---|----------------|--------|
| 1 | `exercices` | API ExerciseDB |
| 2 | `aliments` | Kaggle — Daily Food & Nutrition |
| 3 | `utilisateurs`, `mesures_biometriques` | Kaggle — [Gym Members Exercise (973 lignes)](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset) |
| 4 | `utilisateurs` (complément) | Kaggle — Diet Recommendations |

Les CSV ne sont **pas** dans le dépôt : `etl/data/` est ignoré par Git. Télécharge-les **une fois** sur ta machine.

### Jeux de données Kaggle (liens utiles)

| Fichier local | Page Kaggle | Lignes (données) |
|---------------|-------------|------------------|
| `gym_members_exercise_tracking.csv` | [Gym Members Exercise Dataset](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset) | **973** (+ en-tête) |
| `daily_food_nutrition_dataset.csv` | [Daily Food and Nutrition](https://www.kaggle.com/datasets/adilshamim8/daily-food-and-nutrition-dataset) | variable |
| `diet_recommendations_dataset.csv` | [Diet Recommendations](https://www.kaggle.com/datasets/ziya07/diet-recommendations-dataset) | ~1000 |

Dans l’ETL, les comptes issus du jeu **Gym** ont des e-mails factices uniques de la forme `gym.member.0000@healthai.com` … `gym.member.0972@healthai.com` (un par ligne du CSV, dans l’ordre).

**Vérifier en SQL** (Supabase → SQL Editor) que les 973 comptes gym sont bien là :

```sql
select count(*) from public.utilisateurs
where email like 'gym.member.%@healthai.com';
-- attendu : 973
```

---

## 1. Compte Kaggle + `kaggle.json`

1. [kaggle.com](https://www.kaggle.com) → **Settings** → **API** → **Legacy API Credentials** → **Create New Token**.
2. Place le JSON téléchargé ici (Linux) : `~/.config/kaggle/kaggle.json` (ou `~/.kaggle/kaggle.json`), droits `600`.

Ou : `export KAGGLE_USERNAME=...` et `export KAGGLE_KEY=...` avant le script (le script `download_data.py` peut générer le fichier).

---

## 2. Téléchargement des CSV

```bash
pip install kaggle
python3 etl/download_data.py
```

Fichiers attendus dans `etl/data/` :  
`daily_food_nutrition_dataset.csv`, `gym_members_exercise_tracking.csv`, `diet_recommendations_dataset.csv`.

---

## 3. Lancer l’ETL

Supabase local doit tourner (`supabase start`).

```bash
docker compose up -d etl
docker compose exec etl python scheduler.py run
```

---

## 4. Dépannage rapide

- **403 Kaggle** : accepter les conditions sur la page web du dataset, parfois valider le téléphone sur le compte.
- **CSV introuvable** : relance `python3 etl/download_data.py` depuis la racine du projet.
- **Détails Supabase / ports** : voir [docs/SUPABASE_LOCAL.md](../docs/SUPABASE_LOCAL.md).

*Les recettes côté appli, si la table `recettes` existe, peuvent rester alimentées par un seed SQL d’exemple (`supabase/seed_recettes_demo.sql`), sans ETL Kaggle.*
