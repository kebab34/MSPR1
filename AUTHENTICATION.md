# 🔐 Guide d'authentification avec Supabase

## Configuration

L'authentification utilise maintenant **Supabase Auth** avec le JWT secret de Supabase.

### Variables d'environnement

Le fichier `.env` contient :
```env
JWT_SECRET=g6TmBJR9QCGuhPwCQl/Oi7PYyJ3j7I6fQnoSQwhwZ1N9bPXf8y6D4Ec7OxjrkNyzwE6ypDqrtJ3ljWnneEWPHw==
```

C'est le **Legacy JWT Secret** de votre projet Supabase, utilisé pour vérifier les tokens générés par Supabase Auth.

## Endpoints d'authentification

### 1. Inscription (Sign Up)

**POST** `/api/v1/auth/sign-up`

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "metadata": {
    "name": "John Doe"
  }
}
```

**Réponse :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    ...
  }
}
```

### 2. Connexion (Sign In)

**POST** `/api/v1/auth/sign-in`

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Réponse :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    ...
  }
}
```

### 3. Obtenir l'utilisateur actuel

**GET** `/api/v1/auth/me`

**Headers :**
```
Authorization: Bearer <access_token>
```

**Réponse :**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "user_metadata": {},
    "app_metadata": {},
    "role": "authenticated"
  }
}
```

### 4. Vérifier un token

**GET** `/api/v1/auth/verify`

**Headers :**
```
Authorization: Bearer <access_token>
```

**Réponse :**
```json
{
  "valid": true,
  "payload": {
    "sub": "user-uuid",
    "email": "user@example.com",
    "exp": 1234567890,
    ...
  }
}
```

## Utilisation dans le code

### Vérifier un token dans un endpoint

```python
from fastapi import Header, HTTPException
from app.utils.auth import get_user_from_token

@router.get("/protected")
async def protected_endpoint(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = authorization.split(" ")[1]  # Remove "Bearer "
    user = get_user_from_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"message": f"Hello {user['email']}"}
```

### Utiliser Supabase Auth directement

```python
from app.core.database import supabase

# Sign in
response = supabase.auth.sign_in_with_password({
    "email": "user@example.com",
    "password": "password"
})

# Get user
user = supabase.auth.get_user(response.session.access_token)
```

## Test avec curl

### Inscription
```bash
curl -X POST http://localhost:8000/api/v1/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### Connexion
```bash
curl -X POST http://localhost:8000/api/v1/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### Accéder à un endpoint protégé
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Documentation Supabase Auth

Pour plus d'informations, consultez :
- https://supabase.com/docs/guides/auth
- https://supabase.com/docs/reference/python/auth-signinwithpassword

