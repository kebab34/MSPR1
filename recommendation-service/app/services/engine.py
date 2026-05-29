"""
Moteur de recommandation sportive — appelle Google Gemini (gratuit) pour générer
des programmes d'entraînement personnalisés, puis stocke le résultat en MongoDB.
"""

import json
from datetime import datetime
from google import genai

from app.core.config import settings
from app.core.database import get_db
from app.models.recommendation import (
    WorkoutRequest,
    WorkoutResponse,
    ProgrammeSemaine,
    SeanceEntrainement,
    Exercice,
)

GEMINI_MODEL = "gemini-2.0-flash"
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

_MOCK_EXERCICE = {
    "nom": "Squat",
    "type": "force",
    "series": 3,
    "repetitions": "12",
    "duree_secondes": None,
    "repos_secondes": 60,
    "intensite": "modérée",
    "instructions": "Pieds écartés largeur épaules, descendre jusqu'à 90°, dos droit.",
    "muscles_cibles": ["quadriceps", "fessiers", "ischio-jambiers"],
    "adaptation_limitations": None,
}

def _build_mock_response(req: WorkoutRequest) -> WorkoutResponse:
    jours_actifs = JOURS[: req.jours_par_semaine]
    programme_dict = {}
    for jour in JOURS:
        if jour not in jours_actifs:
            programme_dict[jour] = None
            continue
        programme_dict[jour] = SeanceEntrainement(
            titre=f"Séance {jour.capitalize()} — {req.objectif}",
            duree_estimee_min=req.duree_seance_min,
            echauffement=["5 min de marche rapide", "10 rotations des épaules", "10 fentes dynamiques"],
            exercices_principaux=[Exercice(**_MOCK_EXERCICE), Exercice(
                nom="Pompes",
                type="force",
                series=3,
                repetitions="10",
                duree_secondes=None,
                repos_secondes=60,
                intensite="modérée",
                instructions="Corps gainé, coudes à 45°, descendre jusqu'à frôler le sol.",
                muscles_cibles=["pectoraux", "triceps", "deltoïdes"],
                adaptation_limitations=None,
            )],
            retour_au_calme=["5 min d'étirements", "Respiration abdominale 2 min"],
            calories_estimees=280,
            niveau_difficulte="modéré",
        )
    programme = ProgrammeSemaine(**{j: programme_dict.get(j) for j in JOURS})
    return WorkoutResponse(
        utilisateur_id=req.utilisateur_id,
        objectif=req.objectif,
        programme_semaine=programme,
        conseils_progression=["Augmentez la charge de 5% chaque semaine", "Dormez 7-8h par nuit", "Hydratez-vous avant et après l'effort"],
        conseils_recuperation=["Étirez les groupes musculaires sollicités", "Alternez séances intenses et légères"],
        objectifs_semaine=[f"Réaliser {req.jours_par_semaine} séances complètes", "Atteindre 8000 pas/jour"],
        message_motivant=f"Programme '{req.objectif}' adapté à votre niveau {req.niveau}. Restez régulier ! [MODE DÉMO]",
        created_at=datetime.utcnow(),
    )


def _get_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "Clé API Gemini non configurée. Ajoutez GEMINI_API_KEY dans le fichier .env. "
            "Clé gratuite sur https://aistudio.google.com"
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
        raise ValueError("Réponse IA invalide : JSON introuvable.")
    return json.loads(raw[start:end])


def _build_workout_prompt(req: WorkoutRequest) -> str:
    equip_str = ", ".join(req.equipements_disponibles) if req.equipements_disponibles else "aucun équipement"
    activ_str = ", ".join(req.activites_preferees) if req.activites_preferees else "aucune préférence"
    limit_str = ", ".join(req.limitations_physiques) if req.limitations_physiques else "aucune"
    jours_actifs = JOURS[: req.jours_par_semaine]

    profil = ""
    if req.poids:
        profil += f"\n- Poids : {req.poids} kg"
    if req.age:
        profil += f"\n- Âge : {req.age} ans"
    if req.frequence_cardiaque_repos:
        profil += f"\n- FC repos : {req.frequence_cardiaque_repos} bpm"

    return f"""Génère un programme d'entraînement hebdomadaire personnalisé.

Profil utilisateur :
- Objectif : {req.objectif}
- Niveau : {req.niveau}
- Séances/semaine : {req.jours_par_semaine} ({', '.join(jours_actifs)})
- Durée souhaitée : {req.duree_seance_min} minutes
- Équipements : {equip_str}
- Activités préférées : {activ_str}
- Limitations physiques : {limit_str}{profil}

Réponds UNIQUEMENT avec un JSON valide (sans markdown, sans ```) :
{{
  "programme_semaine": {{
    "lundi": null_ou_seance,
    "mardi": null_ou_seance,
    "mercredi": null_ou_seance,
    "jeudi": null_ou_seance,
    "vendredi": null_ou_seance,
    "samedi": null_ou_seance,
    "dimanche": null_ou_seance
  }},
  "conseils_progression": ["string (3-4 conseils)"],
  "conseils_recuperation": ["string (2-3 conseils)"],
  "objectifs_semaine": ["string (2-3 objectifs mesurables)"],
  "message_motivant": "string (1-2 phrases motivantes)"
}}

Structure d'une séance (remplace null_ou_seance pour les jours actifs : {', '.join(jours_actifs)}) :
{{
  "titre": "string",
  "duree_estimee_min": int,
  "echauffement": ["string"],
  "exercices_principaux": [
    {{
      "nom": "string",
      "type": "cardio|force|souplesse|equilibre",
      "series": int_ou_null,
      "repetitions": "string_ou_null",
      "duree_secondes": int_ou_null,
      "repos_secondes": int,
      "intensite": "faible|modérée|élevée",
      "instructions": "string",
      "muscles_cibles": ["string"],
      "adaptation_limitations": "string_ou_null"
    }}
  ],
  "retour_au_calme": ["string"],
  "calories_estimees": int_ou_null,
  "niveau_difficulte": "facile|modéré|difficile"
}}

Les jours de repos ({', '.join(j for j in JOURS if j not in jours_actifs)}) doivent avoir la valeur null."""


async def generer_programme(req: WorkoutRequest) -> WorkoutResponse:
    if settings.MOCK_AI:
        result = _build_mock_response(req)
        db = get_db()
        doc = result.model_dump()
        doc["programme_semaine"] = {
            jour: (seance.model_dump() if seance else None)
            for jour, seance in result.programme_semaine.__dict__.items()
        }
        inserted = await db["recommendations"].insert_one(doc)
        result.id = str(inserted.inserted_id)
        return result

    client = _get_client()
    prompt = _build_workout_prompt(req)

    try:
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    except Exception as e:
        err = str(e)
        if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
            result = _build_mock_response(req)
            db = get_db()
            doc = result.model_dump()
            doc["programme_semaine"] = {
                jour: (seance.model_dump() if seance else None)
                for jour, seance in result.programme_semaine.__dict__.items()
            }
            inserted = await db["recommendations"].insert_one(doc)
            result.id = str(inserted.inserted_id)
            return result
        raise ValueError(f"Erreur API Gemini : {err}")

    data = _extract_json(response.text)

    programme_dict = {}
    for jour, seance_data in data.get("programme_semaine", {}).items():
        if seance_data is None:
            programme_dict[jour] = None
            continue
        exercices = [Exercice(**e) for e in seance_data.get("exercices_principaux", [])]
        programme_dict[jour] = SeanceEntrainement(
            titre=seance_data["titre"],
            duree_estimee_min=seance_data["duree_estimee_min"],
            echauffement=seance_data.get("echauffement", []),
            exercices_principaux=exercices,
            retour_au_calme=seance_data.get("retour_au_calme", []),
            calories_estimees=seance_data.get("calories_estimees"),
            niveau_difficulte=seance_data.get("niveau_difficulte", "modéré"),
        )

    programme = ProgrammeSemaine(**{j: programme_dict.get(j) for j in JOURS})

    result = WorkoutResponse(
        utilisateur_id=req.utilisateur_id,
        objectif=req.objectif,
        programme_semaine=programme,
        conseils_progression=data.get("conseils_progression", []),
        conseils_recuperation=data.get("conseils_recuperation", []),
        objectifs_semaine=data.get("objectifs_semaine", []),
        message_motivant=data.get("message_motivant", ""),
        created_at=datetime.utcnow(),
    )

    db = get_db()
    doc = result.model_dump()
    doc["programme_semaine"] = {
        jour: (seance.model_dump() if seance else None)
        for jour, seance in result.programme_semaine.__dict__.items()
    }
    inserted = await db["recommendations"].insert_one(doc)
    result.id = str(inserted.inserted_id)

    return result


async def get_historique(utilisateur_id: str, limit: int = 10) -> list[dict]:
    db = get_db()
    cursor = (
        db["recommendations"]
        .find({"utilisateur_id": utilisateur_id})
        .sort("created_at", -1)
        .limit(limit)
    )
    docs = await cursor.to_list(length=limit)
    for doc in docs:
        doc["id"] = str(doc.pop("_id"))
    return docs


async def enregistrer_feedback(feedback_data: dict) -> str:
    db = get_db()
    feedback_data["created_at"] = datetime.utcnow()
    result = await db["feedbacks"].insert_one(feedback_data)
    return str(result.inserted_id)
