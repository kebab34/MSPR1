"""
Endpoints IA pour l'analyse nutritionnelle via Google Gemini (gratuit).
- POST /ai/nutrition/analyze-photo : analyse une photo de repas (vision IA)
- POST /ai/nutrition/meal-plan     : génère un plan de repas personnalisé
"""

import json
import io
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional
from google import genai
import PIL.Image

from app.core.config import settings
from app.api.v1.deps import get_current_user
from app.schemas.nutrition_ai import (
    AnalyseNutritionResponse,
    PlanRepasRequest,
    PlanRepasResponse,
    AlimentDetecte,
    RepasJour,
    ObjectifNutrition,
)

router = APIRouter()

FORMATS_AUTORISES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
TAILLE_MAX_BYTES = 5 * 1024 * 1024  # 5 Mo
GEMINI_MODEL = "gemini-2.0-flash"


def _mock_analyse_response() -> AnalyseNutritionResponse:
    return AnalyseNutritionResponse(
        aliments_detectes=[
            AlimentDetecte(nom="Poulet grillé", quantite_estimee="150 g", calories=165, proteines=31, glucides=0, lipides=3.6, fibres=0),
            AlimentDetecte(nom="Riz basmati", quantite_estimee="120 g (cuit)", calories=156, proteines=3.2, glucides=34, lipides=0.4, fibres=0.6),
            AlimentDetecte(nom="Brocoli vapeur", quantite_estimee="80 g", calories=28, proteines=2.4, glucides=4.4, lipides=0.3, fibres=2.6),
            AlimentDetecte(nom="Huile d'olive", quantite_estimee="5 ml", calories=44, proteines=0, glucides=0, lipides=5, fibres=0),
        ],
        total_calories=393,
        total_proteines=36.6,
        total_glucides=38.4,
        total_lipides=9.3,
        total_fibres=3.2,
        desequilibres_detectes=["Faible apport en fibres", "Manque de légumes verts"],
        suggestions_amelioration=["Ajouter une salade verte", "Augmenter la portion de légumes à 200 g", "Ajouter des légumineuses pour plus de fibres"],
        score_nutritionnel=78,
        message_global="Repas équilibré avec un bon apport en protéines maigres. Augmentez la part de légumes pour un meilleur équilibre nutritionnel. [MODE DÉMO]",
    )


def _mock_meal_plan_response(req: "PlanRepasRequest") -> "PlanRepasResponse":
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][: req.nb_jours]
    plan = {
        j: RepasJour(
            petit_dejeuner="Flocons d'avoine, lait demi-écrémé, banane, miel",
            dejeuner="Escalope de dinde grillée, quinoa, haricots verts",
            diner="Saumon au four, patate douce, épinards sautés",
            collations="Yaourt grec, amandes",
            calories_estimees=2100,
            proteines_estimees=145,
            glucides_estimees=220,
            lipides_estimees=65,
        )
        for j in jours
    }
    return PlanRepasResponse(
        plan=plan,
        calories_moyennes_par_jour=2100,
        conseils_generaux=["Boire 1,5 à 2 L d'eau par jour", "Éviter les aliments ultra-transformés", "Répartir les repas toutes les 3-4 heures"],
        liste_courses=["Flocons d'avoine", "Lait demi-écrémé", "Bananes", "Escalope de dinde", "Quinoa", "Haricots verts", "Saumon", "Patate douce", "Épinards", "Yaourt grec", "Amandes"],
        message_personnalise=f"Plan personnalisé pour votre objectif '{req.objectif}'. Adapté à vos besoins nutritionnels. [MODE DÉMO]",
    )


def _get_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Clé API Gemini non configurée. Ajoutez GEMINI_API_KEY dans le fichier .env. "
                   "Clé gratuite sur https://aistudio.google.com",
        )
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise HTTPException(status_code=502, detail="Réponse IA invalide : JSON introuvable.")
    try:
        return json.loads(raw[start:end])
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"Réponse IA non parsable : {e}")


def _build_analyse_prompt(objectif: str, allergies: list[str], notes: Optional[str]) -> str:
    allergies_str = ", ".join(allergies) if allergies else "aucune"
    notes_str = f"\nNotes : {notes}" if notes else ""
    return f"""Analyse cette photo de repas et fournis une réponse JSON structurée.

Contexte :
- Objectif santé : {objectif}
- Allergies : {allergies_str}{notes_str}

Réponds UNIQUEMENT avec un objet JSON valide (sans markdown, sans ```) :
{{
  "aliments_detectes": [
    {{
      "nom": "string",
      "quantite_estimee": "string",
      "calories": float,
      "proteines": float,
      "glucides": float,
      "lipides": float,
      "fibres": float
    }}
  ],
  "total_calories": float,
  "total_proteines": float,
  "total_glucides": float,
  "total_lipides": float,
  "total_fibres": float,
  "desequilibres_detectes": ["string"],
  "suggestions_amelioration": ["string"],
  "score_nutritionnel": int,
  "message_global": "string"
}}
Valeurs en grammes sauf calories (kcal). Score de 0 à 100."""


def _build_meal_plan_prompt(req: PlanRepasRequest) -> str:
    jours = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"][: req.nb_jours]
    allergies_str = ", ".join(req.allergies) if req.allergies else "aucune"
    budget_str = f"{req.budget_quotidien} €/jour" if req.budget_quotidien else "non précisé"
    regime_str = req.regime or "aucun"
    calories_str = f"{req.calories_cibles} kcal/jour" if req.calories_cibles else "à calculer"
    jours_json = ", ".join(f'"{j}": {{...}}' for j in jours)

    return f"""Génère un plan de repas personnalisé sur {req.nb_jours} jours.

- Objectif : {req.objectif}
- Calories : {calories_str}
- Budget : {budget_str}
- Allergies : {allergies_str}
- Régime : {regime_str}

Réponds UNIQUEMENT avec un JSON valide (sans markdown, sans ```) :
{{
  "plan": {{ {jours_json} }},
  "calories_moyennes_par_jour": float,
  "conseils_generaux": ["string"],
  "liste_courses": ["string"],
  "message_personnalise": "string"
}}

Chaque jour (structure exacte) :
{{
  "petit_dejeuner": "string",
  "dejeuner": "string",
  "diner": "string",
  "collations": "string ou null",
  "calories_estimees": float,
  "proteines_estimees": float,
  "glucides_estimees": float,
  "lipides_estimees": float
}}"""


@router.post("/analyze-photo", response_model=AnalyseNutritionResponse, status_code=200)
async def analyser_photo_repas(
    photo: UploadFile = File(...),
    objectif: ObjectifNutrition = Form(ObjectifNutrition.EQUILIBRE),
    allergies: str = Form(""),
    notes_utilisateur: Optional[str] = Form(None),
    _u: dict = Depends(get_current_user),
):
    """Analyse une photo de repas avec Google Gemini Vision (gratuit)."""
    if photo.content_type not in FORMATS_AUTORISES:
        raise HTTPException(status_code=415, detail=f"Format non supporté : {photo.content_type}.")

    contenu = await photo.read()
    if len(contenu) > TAILLE_MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image trop lourde (max 5 Mo).")

    try:
        pil_image = PIL.Image.open(io.BytesIO(contenu))
    except Exception:
        raise HTTPException(status_code=422, detail="Impossible de lire l'image.")

    if settings.MOCK_AI:
        return _mock_analyse_response()

    allergies_list = [a.strip() for a in allergies.split(",") if a.strip()] if allergies else []
    prompt = _build_analyse_prompt(objectif.value, allergies_list, notes_utilisateur)

    client = _get_client()
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[pil_image, prompt],
        )
    except Exception as e:
        err = str(e)
        if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
            return _mock_analyse_response()
        raise HTTPException(status_code=502, detail=f"Erreur API Gemini : {err}")

    data = _extract_json(response.text)

    try:
        aliments = [AlimentDetecte(**a) for a in data.get("aliments_detectes", [])]
        return AnalyseNutritionResponse(
            aliments_detectes=aliments,
            total_calories=data.get("total_calories", 0),
            total_proteines=data.get("total_proteines", 0),
            total_glucides=data.get("total_glucides", 0),
            total_lipides=data.get("total_lipides", 0),
            total_fibres=data.get("total_fibres", 0),
            desequilibres_detectes=data.get("desequilibres_detectes", []),
            suggestions_amelioration=data.get("suggestions_amelioration", []),
            score_nutritionnel=max(0, min(100, int(data.get("score_nutritionnel", 50)))),
            message_global=data.get("message_global", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Données IA incorrectes : {e}")


@router.post("/meal-plan", response_model=PlanRepasResponse, status_code=200)
async def generer_plan_repas(
    req: PlanRepasRequest,
    _u: dict = Depends(get_current_user),
):
    """Génère un plan de repas personnalisé avec Google Gemini (gratuit)."""
    if settings.MOCK_AI:
        return _mock_meal_plan_response(req)

    client = _get_client()
    prompt = _build_meal_plan_prompt(req)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
    except Exception as e:
        err = str(e)
        if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
            return _mock_meal_plan_response(req)
        raise HTTPException(status_code=502, detail=f"Erreur API Gemini : {err}")

    data = _extract_json(response.text)

    try:
        plan_parse = {jour: RepasJour(**repas) for jour, repas in data.get("plan", {}).items()}
        return PlanRepasResponse(
            plan=plan_parse,
            calories_moyennes_par_jour=data.get("calories_moyennes_par_jour", 0),
            conseils_generaux=data.get("conseils_generaux", []),
            liste_courses=data.get("liste_courses", []),
            message_personnalise=data.get("message_personnalise", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Données IA incorrectes : {e}")
