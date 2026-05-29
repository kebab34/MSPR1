"""
ETL Scheduler — pipeline d'ingestion et de transformation automatisé.

Modes d'exécution :
  python scheduler.py        → démarre le scheduler (exécution immédiate + cron)
  python scheduler.py run    → exécution unique (debug / CI)

Logs :
  - stdout (console Docker)
  - etl/logs/etl_YYYY-MM-DD.log  (rotation journalière)

Rapports d'exécution :
  - etl/logs/reports/report_YYYY-MM-DD_HH-MM-SS.json
    Contient : timestamp, durée, statut de chaque source, nombre de lignes,
    liste d'erreurs, résultat global (success / partial / failure).
"""

import json        # pour écrire les rapports d'exécution au format JSON
import logging     # pour afficher et enregistrer des messages de log
import os          # pour lire les variables d'environnement (.env)
import sys         # pour lire les arguments passés en ligne de commande (ex: "run")
import time        # importé mais non utilisé directement
import traceback   # pour capturer le détail complet d'une erreur Python
from datetime import datetime, timezone                   # pour horodater les logs et rapports
from logging.handlers import TimedRotatingFileHandler     # pour créer un nouveau fichier de log chaque jour
from pathlib import Path                                  # pour construire les chemins de fichiers proprement

import pandas as pd                                        # librairie de manipulation de données (DataFrames)
from apscheduler.schedulers.blocking import BlockingScheduler  # scheduler qui bloque le processus (tourne en continu)
from apscheduler.triggers.cron import CronTrigger              # permet de définir une heure de déclenchement type cron Linux
from dotenv import load_dotenv                                  # lit le fichier .env et charge les variables d'environnement

from download_data import DATA_DIR, DATASETS, download_datasets                  # fonctions de téléchargement des CSV Kaggle
from extract import extract_exercises_from_exercisedb, extract_from_csv          # fonctions de lecture des données brutes
from load import SupabaseLoader                                                  # classe qui écrit dans Supabase
from transform import (
    clean_data,                              # supprime les doublons et les lignes vides
    restore_list_columns,                    # reconvertit les strings "['x']" en vraies listes Python
    transform_diet_reco_to_utilisateurs,     # transforme le dataset Diet → table utilisateurs
    transform_exercises_from_exercisedb,     # transforme les exercices → table exercices
    transform_gym_members_to_mesures,        # transforme Gym Members → table mesures_biometriques
    transform_gym_members_to_utilisateurs,   # transforme Gym Members → table utilisateurs
    transform_nutrition_dataset,             # transforme le dataset nutrition → table aliments
    validate_data,                           # vérifie que les colonnes obligatoires sont présentes
)

load_dotenv()  # charge toutes les variables du fichier .env dans l'environnement Python

# ---------------------------------------------------------------------------
# Répertoires de logs
# ---------------------------------------------------------------------------
LOGS_DIR = Path(__file__).parent / "logs"          # chemin du dossier etl/logs/
REPORTS_DIR = LOGS_DIR / "reports"                 # chemin du dossier etl/logs/reports/
LOGS_DIR.mkdir(exist_ok=True)                       # crée le dossier logs/ s'il n'existe pas
REPORTS_DIR.mkdir(exist_ok=True)                    # crée le dossier reports/ s'il n'existe pas

# ---------------------------------------------------------------------------
# Configuration du logger (stdout + fichier tournant)
# ---------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"  # format de chaque ligne de log
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"                                   # format de la date dans les logs

logger = logging.getLogger("etl")   # crée un logger nommé "etl"
logger.setLevel(logging.DEBUG)      # capture tous les niveaux (DEBUG, INFO, WARNING, ERROR)

if not logger.handlers:  # évite d'ajouter les handlers en double si ce module est importé plusieurs fois
    # Handler 1 : affiche les logs dans le terminal Docker (niveau INFO minimum)
    _console = logging.StreamHandler(sys.stdout)
    _console.setLevel(logging.INFO)                                        # n'affiche pas les DEBUG dans la console
    _console.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))      # applique le format défini
    logger.addHandler(_console)                                            # attache le handler au logger

    # Handler 2 : écrit les logs dans un fichier (niveau DEBUG, tout est enregistré)
    _log_file = LOGS_DIR / f"etl_{datetime.now().strftime('%Y-%m-%d')}.log"  # nom du fichier avec la date du jour
    _file = TimedRotatingFileHandler(
        _log_file, when="midnight", backupCount=30, encoding="utf-8"  # nouveau fichier à minuit, garde 30 jours
    )
    _file.setLevel(logging.DEBUG)                                          # enregistre tout, même les DEBUG
    _file.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(_file)


# ---------------------------------------------------------------------------
# Rapport d'exécution
# ---------------------------------------------------------------------------

class ExecutionReport:
    """Collecte les métriques de chaque source et génère un rapport JSON à la fin du pipeline."""

    def __init__(self):
        self.started_at = datetime.now(timezone.utc)  # heure de début du pipeline (UTC)
        self.sources: list[dict] = []                  # liste des résultats par source
        self._errors: list[str] = []                   # liste des erreurs accumulées

    def record_source(self, name: str, rows: int, ok: bool, error: str | None = None):
        """Enregistre le résultat d'une source (succès ou échec)."""
        entry = {"source": name, "rows_loaded": rows, "success": ok}  # crée un objet résultat
        if error:
            entry["error"] = error                                      # ajoute le message d'erreur si présent
            self._errors.append(f"[{name}] {error}")                   # mémorise l'erreur dans la liste globale
        self.sources.append(entry)                                      # ajoute le résultat à la liste
        if ok:
            logger.info("  ✅ %s — %d ligne(s) chargée(s)", name, rows)   # log succès
        else:
            logger.error("  ❌ %s — %s", name, error or "erreur inconnue")  # log échec

    def save(self):
        """Calcule la durée totale, détermine le statut global et sauvegarde le rapport JSON."""
        finished_at = datetime.now(timezone.utc)                                          # heure de fin
        duration_s = round((finished_at - self.started_at).total_seconds(), 2)            # durée en secondes

        all_ok = all(s["success"] for s in self.sources)    # True si toutes les sources ont réussi
        any_ok = any(s["success"] for s in self.sources)    # True si au moins une source a réussi
        status = "success" if all_ok else ("partial" if any_ok else "failure")  # statut global

        payload = {
            "started_at": self.started_at.isoformat(),    # horodatage de début au format ISO
            "finished_at": finished_at.isoformat(),        # horodatage de fin
            "duration_seconds": duration_s,                # durée totale
            "status": status,                              # "success", "partial" ou "failure"
            "sources": self.sources,                       # détail par source
            "errors": self._errors,                        # liste de toutes les erreurs
        }

        ts = self.started_at.strftime("%Y-%m-%d_%H-%M-%S")         # timestamp pour le nom du fichier
        report_path = REPORTS_DIR / f"report_{ts}.json"             # chemin complet du rapport
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)     # écrit le rapport JSON indenté

        logger.info(
            "Rapport sauvegardé : %s (statut=%s, durée=%.1fs)",
            report_path.name, status, duration_s,
        )
        return payload  # retourne le rapport pour pouvoir le lire après l'appel


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def run_etl_pipeline():
    """
    Lance le pipeline ETL complet sur les 4 sources :
      1. ExerciseDB API → exercices
      2. Daily Food & Nutrition (Kaggle) → aliments
      3. Gym Members Exercise (Kaggle) → utilisateurs + mesures_biometriques
      4. Diet Recommendations (Kaggle) → utilisateurs
    """
    logger.info("=" * 60)
    logger.info("Démarrage du pipeline ETL — %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("=" * 60)

    report = ExecutionReport()  # crée un nouvel objet rapport pour cette exécution

    # ------------------------------------------------------------------
    # Téléchargement automatique des datasets Kaggle manquants
    # ------------------------------------------------------------------
    missing = [
        ds["file"] for ds in DATASETS               # liste les fichiers attendus
        if not os.path.exists(os.path.join(DATA_DIR, ds["file"]))  # qui ne sont pas encore présents
    ]
    if missing:
        logger.info("Fichiers manquants : %s — lancement du téléchargement Kaggle…", missing)
        try:
            download_datasets()  # télécharge les fichiers manquants via l'API Kaggle
        except RuntimeError as exc:
            logger.warning("Téléchargement Kaggle impossible : %s", exc)
            logger.warning(
                "Placez les CSV manuellement dans etl/data/ "
                "ou définissez KAGGLE_USERNAME + KAGGLE_KEY dans .env"
            )

    loader = SupabaseLoader()  # crée la connexion à Supabase (lit SUPABASE_URL et SUPABASE_KEY du .env)

    # ------------------------------------------------------------------
    # 1. EXERCICES — ExerciseDB API
    # ------------------------------------------------------------------
    logger.info("\n[1/4] Extraction des exercices (ExerciseDB API)…")
    try:
        df_ex = extract_exercises_from_exercisedb(limit=200)      # récupère 200 exercices depuis l'API
        df_ex = transform_exercises_from_exercisedb(df_ex)         # transforme les colonnes vers notre schéma
        df_ex = clean_data(df_ex)                                  # supprime les doublons et lignes vides

        if validate_data(df_ex, ["nom"]):                          # vérifie que la colonne "nom" est présente
            ok = loader.upsert_dataframe(df_ex, "exercices", on_conflict="nom")  # charge en base (upsert sur le nom)
            report.record_source("exercices", len(df_ex), bool(ok))
        else:
            report.record_source("exercices", 0, False, "Validation échouée (colonne 'nom' manquante)")
    except Exception as exc:
        report.record_source("exercices", 0, False, traceback.format_exc(limit=3))  # capture les 3 dernières lignes d'erreur
        logger.debug("Traceback complet :", exc_info=True)

    # ------------------------------------------------------------------
    # 2. ALIMENTS — Daily Food & Nutrition Dataset (Kaggle)
    # ------------------------------------------------------------------
    logger.info("\n[2/4] Extraction aliments (Daily Food & Nutrition Dataset)…")
    nutrition_path = os.path.join(DATA_DIR, "daily_food_nutrition_dataset.csv")  # chemin du CSV
    try:
        df_nutrition = extract_from_csv(nutrition_path)            # lit le CSV dans un DataFrame
        df_aliments = transform_nutrition_dataset(df_nutrition)    # transforme vers le schéma aliments
        df_aliments = clean_data(df_aliments)                      # nettoie les données

        if validate_data(df_aliments, ["nom", "calories"]):        # vérifie les colonnes obligatoires
            ok = loader.upsert_dataframe(df_aliments, "aliments", on_conflict="nom")  # upsert sur le nom
            report.record_source("aliments", len(df_aliments), bool(ok))
        else:
            report.record_source("aliments", 0, False, "Validation échouée (colonnes 'nom'/'calories')")
    except Exception as exc:
        report.record_source("aliments", 0, False, traceback.format_exc(limit=3))
        logger.debug("Traceback complet :", exc_info=True)

    # ------------------------------------------------------------------
    # 3. UTILISATEURS + MESURES — Gym Members Exercise Dataset (Kaggle)
    # ------------------------------------------------------------------
    logger.info("\n[3/4] Extraction utilisateurs (Gym Members Exercise Dataset)…")
    gym_path = os.path.join(DATA_DIR, "gym_members_exercise_tracking.csv")
    try:
        df_gym = extract_from_csv(gym_path)  # lit le CSV

        # 3a. Insère les utilisateurs en premier
        df_gym_users = transform_gym_members_to_utilisateurs(df_gym)  # transforme → schéma utilisateurs
        df_gym_users = clean_data(df_gym_users)                        # nettoie
        df_gym_users = restore_list_columns(df_gym_users, ["objectifs"])  # reconvertit la colonne objectifs en liste

        if validate_data(df_gym_users, ["email"]):
            ok = loader.upsert_dataframe(df_gym_users, "utilisateurs", on_conflict="email")  # upsert sur l'email
            report.record_source("utilisateurs_gym", len(df_gym_users), bool(ok))
        else:
            report.record_source("utilisateurs_gym", 0, False, "Validation échouée (colonne 'email')")

        # 3b. Récupère les UUIDs générés par Supabase pour lier les mesures aux utilisateurs
        logger.info("Récupération des UUIDs pour les mesures biométriques…")
        gym_emails = list(df_gym_users["email"].dropna().unique())  # liste de tous les emails uniques
        email_to_id: dict[str, str] = {}                             # dictionnaire email → UUID

        # Requête par lot de 100 (limite par défaut de l'API Supabase)
        for i in range(0, len(gym_emails), 100):
            batch = gym_emails[i : i + 100]                          # extrait un lot de 100 emails
            res = (
                loader.client.table("utilisateurs")
                .select("id_utilisateur,email")                       # sélectionne uniquement ces deux colonnes
                .in_("email", batch)                                  # filtre WHERE email IN (...)
                .execute()
            )
            for row in res.data:
                email_to_id[row["email"]] = row["id_utilisateur"]    # mappe email → UUID

        logger.info("  %d/%d utilisateurs retrouvés pour les mesures", len(email_to_id), len(gym_emails))

        # 3c. Transforme et charge les mesures biométriques
        df_mesures = transform_gym_members_to_mesures(df_gym, email_to_id)  # transforme → schéma mesures
        if len(df_mesures) > 0:
            ok = loader.load_dataframe(df_mesures, "mesures_biometriques")  # insert simple (pas d'upsert)
            report.record_source("mesures_biometriques", len(df_mesures), bool(ok))
        else:
            report.record_source("mesures_biometriques", 0, False, "Aucune mesure à charger")

    except Exception as exc:
        report.record_source("gym_members", 0, False, traceback.format_exc(limit=3))
        logger.debug("Traceback complet :", exc_info=True)

    # ------------------------------------------------------------------
    # 4. UTILISATEURS — Diet Recommendations Dataset (Kaggle)
    # ------------------------------------------------------------------
    logger.info("\n[4/4] Extraction utilisateurs (Diet Recommendations Dataset)…")
    diet_path = os.path.join(DATA_DIR, "diet_recommendations_dataset.csv")
    try:
        df_diet = extract_from_csv(diet_path)                              # lit le CSV
        df_diet_users = transform_diet_reco_to_utilisateurs(df_diet)       # transforme → schéma utilisateurs
        df_diet_users = clean_data(df_diet_users)                          # nettoie
        df_diet_users = restore_list_columns(df_diet_users, ["objectifs"]) # reconvertit la liste objectifs

        if validate_data(df_diet_users, ["email"]):
            ok = loader.upsert_dataframe(df_diet_users, "utilisateurs", on_conflict="email")
            report.record_source("utilisateurs_diet", len(df_diet_users), bool(ok))
        else:
            report.record_source("utilisateurs_diet", 0, False, "Validation échouée (colonne 'email')")
    except Exception as exc:
        report.record_source("utilisateurs_diet", 0, False, traceback.format_exc(limit=3))
        logger.debug("Traceback complet :", exc_info=True)

    # ------------------------------------------------------------------
    # Clôture : sauvegarde du rapport et log du statut final
    # ------------------------------------------------------------------
    logger.info("\n" + "=" * 60)
    payload = report.save()  # sauvegarde le rapport JSON et retourne son contenu
    logger.info("Pipeline ETL terminé — statut : %s", payload["status"].upper())
    logger.info("=" * 60)
    return payload  # retourne le rapport (utile pour les tests)


# ---------------------------------------------------------------------------
# Scheduler (mode continu)
# ---------------------------------------------------------------------------

def _parse_schedule(expr: str) -> CronTrigger:
    """
    Convertit une expression cron 5-champs en objet CronTrigger APScheduler.
    Format : 'minute heure jour mois jour_semaine'
    Exemple : '0 2 * * 1' → tous les lundis à 02h00 UTC
    """
    parts = expr.strip().split()     # découpe l'expression en liste de 5 parties
    if len(parts) == 5:
        minute, hour, day, month, day_of_week = parts  # déstructure les 5 champs
        return CronTrigger(
            minute=minute, hour=hour, day=day,
            month=month, day_of_week=day_of_week,
        )
    # Expression invalide → on utilise le planning par défaut (lundi 02h00)
    logger.warning("Expression cron invalide '%s' — fallback : 0 2 * * 1 (lundi 02h00)", expr)
    return CronTrigger(minute=0, hour=2, day_of_week=1)


def main():
    """
    Démarre le scheduler APScheduler en mode continu.
    - Lance le pipeline immédiatement au démarrage (pour valider que tout fonctionne)
    - Puis le relance automatiquement selon le planning défini par ETL_SCHEDULE
    """
    schedule = os.getenv("ETL_SCHEDULE", "0 2 * * 1")  # lit le planning depuis .env, défaut = lundi 02h00
    trigger = _parse_schedule(schedule)                  # convertit en objet CronTrigger

    scheduler = BlockingScheduler(timezone="UTC")        # crée le scheduler en UTC
    scheduler.add_job(
        run_etl_pipeline,         # fonction à exécuter
        trigger=trigger,           # quand l'exécuter (planning cron)
        id="etl_job",              # identifiant unique du job
        name="ETL Pipeline",       # nom affiché dans les logs
        replace_existing=True,     # remplace le job si déjà enregistré
        misfire_grace_time=3600,   # tolère jusqu'à 1h de retard (ex: restart Docker)
    )

    logger.info("ETL scheduler démarré — planification : %s", schedule)
    logger.info("Répertoire des logs    : %s", LOGS_DIR.resolve())
    logger.info("Répertoire des rapports: %s", REPORTS_DIR.resolve())

    # Lance le pipeline une première fois immédiatement au démarrage
    logger.info("Exécution immédiate au démarrage…")
    run_etl_pipeline()

    logger.info("Prochaine exécution planifiée selon cron : %s", schedule)
    logger.info("Appuyez sur Ctrl+C pour arrêter.")

    try:
        scheduler.start()  # démarre la boucle infinie du scheduler (bloque le processus)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler arrêté proprement.")
        scheduler.shutdown()  # arrête proprement le scheduler sans forcer


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Si on passe l'argument "run", exécute le pipeline une seule fois (mode debug/CI)
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        logger.info("Mode exécution unique (argument 'run')…")
        run_etl_pipeline()  # une seule exécution puis le script se termine
    else:
        main()  # mode normal : exécution immédiate + scheduler continu
