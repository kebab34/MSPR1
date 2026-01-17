#!/usr/bin/env python3
"""
Script de test pour les endpoints de l'API FastAPI
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

def test_health_endpoint():
    """Teste l'endpoint de santé"""
    print("\n🔍 Test endpoint /health...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health check OK: {response.json()}")
            return True
        else:
            print(f"❌ Health check échoué: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Impossible de se connecter à l'API sur {API_URL}")
        print("   Assurez-vous que l'API est démarrée (docker-compose up ou uvicorn)")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_api_v1_health():
    """Teste l'endpoint de santé v1"""
    print("\n🔍 Test endpoint /api/v1/health...")
    try:
        response = requests.get(f"{API_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ API v1 health OK: {response.json()}")
            return True
        else:
            print(f"❌ API v1 health échoué: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_get_aliments():
    """Teste l'endpoint GET /api/v1/aliments"""
    print("\n🔍 Test endpoint GET /api/v1/aliments...")
    try:
        response = requests.get(f"{API_URL}/api/v1/aliments", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Liste des aliments récupérée: {len(data)} aliments")
            return True
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_get_exercices():
    """Teste l'endpoint GET /api/v1/exercices"""
    print("\n🔍 Test endpoint GET /api/v1/exercices...")
    try:
        response = requests.get(f"{API_URL}/api/v1/exercices", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Liste des exercices récupérée: {len(data)} exercices")
            return True
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_get_utilisateurs():
    """Teste l'endpoint GET /api/v1/utilisateurs"""
    print("\n🔍 Test endpoint GET /api/v1/utilisateurs...")
    try:
        response = requests.get(f"{API_URL}/api/v1/utilisateurs", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Liste des utilisateurs récupérée: {len(data)} utilisateurs")
            return True
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_docs():
    """Teste l'accès à la documentation"""
    print("\n🔍 Test accès à la documentation...")
    try:
        response = requests.get(f"{API_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Documentation accessible sur /docs")
            return True
        else:
            print(f"⚠️  Documentation non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Erreur: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("=" * 60)
    print("🧪 TEST DES ENDPOINTS DE L'API FASTAPI")
    print("=" * 60)
    print(f"\n📍 URL de l'API: {API_URL}")
    
    tests = [
        ("Health check", test_health_endpoint),
        ("API v1 health", test_api_v1_health),
        ("GET aliments", test_get_aliments),
        ("GET exercices", test_get_exercices),
        ("GET utilisateurs", test_get_utilisateurs),
        ("Documentation", test_docs),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erreur lors du test {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n📈 Résultat: {passed}/{total} tests passés")
    
    if passed == total:
        print("\n✅ TOUS LES TESTS SONT PASSÉS !")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) ont échoué")
        print("\n💡 Assurez-vous que:")
        print("   1. L'API est démarrée (docker-compose up ou uvicorn)")
        print("   2. Les variables d'environnement sont correctement configurées")
        print("   3. Supabase est accessible")
        return 1

if __name__ == "__main__":
    sys.exit(main())


