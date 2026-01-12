# 📡 Documentation des Endpoints API

## Vue d'ensemble

L'API FastAPI expose les endpoints REST pour gérer toutes les entités du système de santé connectée.

**Base URL** : `http://localhost:8000`  
**Documentation interactive** : `http://localhost:8000/docs`  
**ReDoc** : `http://localhost:8000/redoc`

---

## 🔗 Endpoints disponibles

### Health Check

- `GET /health` - Vérification de santé de l'API
- `GET /api/v1/health` - Vérification de santé API v1

---

### 👤 Utilisateurs

**Base path** : `/api/v1/utilisateurs`

- `GET /api/v1/utilisateurs` - Liste des utilisateurs
  - Query params: `skip`, `limit`, `type_abonnement`
- `GET /api/v1/utilisateurs/{utilisateur_id}` - Détails d'un utilisateur
- `POST /api/v1/utilisateurs` - Créer un utilisateur
- `PUT /api/v1/utilisateurs/{utilisateur_id}` - Mettre à jour un utilisateur
- `DELETE /api/v1/utilisateurs/{utilisateur_id}` - Supprimer un utilisateur

**Exemple de création** :
```json
{
  "email": "user@example.com",
  "nom": "Dupont",
  "prenom": "Jean",
  "age": 30,
  "sexe": "M",
  "poids": 75.5,
  "taille": 180.0,
  "objectifs": ["perte_poids", "endurance"],
  "type_abonnement": "premium"
}
```

---

### 🥗 Aliments

**Base path** : `/api/v1/aliments`

- `GET /api/v1/aliments` - Liste des aliments
  - Query params: `skip`, `limit`, `search`
- `GET /api/v1/aliments/{aliment_id}` - Détails d'un aliment
- `POST /api/v1/aliments` - Créer un aliment
- `PUT /api/v1/aliments/{aliment_id}` - Mettre à jour un aliment
- `DELETE /api/v1/aliments/{aliment_id}` - Supprimer un aliment

**Exemple de création** :
```json
{
  "nom": "Pomme",
  "calories": 52.0,
  "proteines": 0.3,
  "glucides": 14.0,
  "lipides": 0.2,
  "fibres": 2.4,
  "unite": "100g",
  "source": "Kaggle"
}
```

---

### 🏋️ Exercices

**Base path** : `/api/v1/exercices`

- `GET /api/v1/exercices` - Liste des exercices
  - Query params: `skip`, `limit`, `type`, `groupe_musculaire`, `niveau`, `search`
- `GET /api/v1/exercices/{exercice_id}` - Détails d'un exercice
- `POST /api/v1/exercices` - Créer un exercice
- `PUT /api/v1/exercices/{exercice_id}` - Mettre à jour un exercice
- `DELETE /api/v1/exercices/{exercice_id}` - Supprimer un exercice

**Exemple de création** :
```json
{
  "nom": "Pompes",
  "type": "force",
  "groupe_musculaire": "pectoraux",
  "niveau": "debutant",
  "equipement": "aucun",
  "description": "Exercice de musculation au poids du corps",
  "source": "ExerciseDB API"
}
```

---

### 📝 Journal Alimentaire

**Base path** : `/api/v1/journal`

- `GET /api/v1/journal` - Liste des entrées du journal
  - Query params: `utilisateur_id`, `date_debut`, `date_fin`, `skip`, `limit`
- `GET /api/v1/journal/{journal_id}` - Détails d'une entrée
- `POST /api/v1/journal` - Créer une entrée
- `PUT /api/v1/journal/{journal_id}` - Mettre à jour une entrée
- `DELETE /api/v1/journal/{journal_id}` - Supprimer une entrée

**Exemple de création** :
```json
{
  "id_utilisateur": "uuid-here",
  "id_aliment": "uuid-here",
  "date": "2024-01-15",
  "heure": "08:00:00",
  "quantite": 150.0,
  "calories_totales": 78.0,
  "repas": "petit_dejeuner"
}
```

---

### 🏃 Sessions Sport

**Base path** : `/api/v1/sessions`

- `GET /api/v1/sessions` - Liste des sessions
  - Query params: `utilisateur_id`, `date_debut`, `date_fin`, `skip`, `limit`
- `GET /api/v1/sessions/{session_id}` - Détails d'une session
- `POST /api/v1/sessions` - Créer une session (avec exercices optionnels)
- `PUT /api/v1/sessions/{session_id}` - Mettre à jour une session
- `DELETE /api/v1/sessions/{session_id}` - Supprimer une session

**Exemple de création avec exercices** :
```json
{
  "id_utilisateur": "uuid-here",
  "date": "2024-01-15",
  "heure_debut": "18:00:00",
  "heure_fin": "19:00:00",
  "duree_minutes": 60,
  "intensite": "moderee",
  "calories_brûlees": 350.0,
  "exercices": [
    {
      "id_exercice": "uuid-here",
      "serie": 1,
      "repetitions": 15,
      "poids": 0.0,
      "repos_secondes": 60,
      "ordre": 1
    }
  ]
}
```

---

### ❤️ Mesures Biométriques

**Base path** : `/api/v1/mesures`

- `GET /api/v1/mesures` - Liste des mesures
  - Query params: `utilisateur_id`, `date_debut`, `date_fin`, `skip`, `limit`
- `GET /api/v1/mesures/{mesure_id}` - Détails d'une mesure
- `POST /api/v1/mesures` - Créer une mesure
- `PUT /api/v1/mesures/{mesure_id}` - Mettre à jour une mesure
- `DELETE /api/v1/mesures/{mesure_id}` - Supprimer une mesure

**Exemple de création** :
```json
{
  "id_utilisateur": "uuid-here",
  "date": "2024-01-15",
  "poids": 75.2,
  "frequence_cardiaque_rest": 65,
  "duree_sommeil_heures": 7.5,
  "qualite_sommeil": 8,
  "calories_brûlees_jour": 2200.0,
  "pas": 8500
}
```

---

## 🧪 Tester l'API

### Avec la documentation interactive

1. Démarrer l'API :
   ```bash
   docker-compose up api
   # ou
   cd api && uvicorn app.main:app --reload
   ```

2. Ouvrir `http://localhost:8000/docs` dans votre navigateur

3. Tester les endpoints directement depuis l'interface Swagger

### Avec curl

```bash
# Health check
curl http://localhost:8000/health

# Liste des aliments
curl http://localhost:8000/api/v1/aliments

# Créer un aliment
curl -X POST http://localhost:8000/api/v1/aliments \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Banane",
    "calories": 89.0,
    "proteines": 1.1,
    "glucides": 23.0,
    "lipides": 0.3
  }'
```

### Avec le script de test

```bash
python3 test/api/test_api_endpoints.py
```

---

## 📝 Notes importantes

- Tous les endpoints utilisent **Supabase** comme backend
- Les opérations utilisent la **service key** pour les droits administrateur
- Les UUIDs sont utilisés pour tous les IDs
- Les dates sont au format ISO (YYYY-MM-DD)
- Les heures sont au format HH:MM:SS

---

## 🔒 Sécurité

⚠️ **Important** : Actuellement, l'API utilise la service key pour toutes les opérations. Pour la production, il faudra :
- Implémenter l'authentification JWT
- Utiliser RLS (Row Level Security) dans Supabase
- Filtrer les données selon l'utilisateur connecté

