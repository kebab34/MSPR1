# Tests

Ce dossier contient tous les scripts et fichiers de test du projet.

## Structure

```
test/
├── README.md                    # Ce fichier
├── test_config.sh              # Script de test de configuration globale
└── supabase/                   # Tests spécifiques à Supabase
    └── test_supabase_connection.py
```

## Scripts disponibles

### `test_config.sh`
Script de test de la configuration globale du projet :
- Vérification de Docker
- Vérification du fichier `.env`
- Vérification des variables d'environnement
- Vérification de la structure du projet

**Usage :**
```bash
./test/test_config.sh
```

### `supabase/test_supabase_connection.py`
Script de test de connexion à Supabase :
- Vérification des variables d'environnement Supabase
- Test de connexion au client Supabase
- Test de l'API Supabase

**Usage :**
```bash
python3 test/supabase/test_supabase_connection.py
```

## Ajouter de nouveaux tests

Pour ajouter de nouveaux tests :
1. Créer un sous-dossier dans `test/` pour le domaine concerné
2. Ajouter vos scripts de test
3. Documenter dans ce README

