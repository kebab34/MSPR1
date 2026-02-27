"""
ETL Scheduler
Schedule and run ETL jobs
"""
import os
import logging
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from extract import extract_from_csv, extract_from_excel, extract_from_api, extract_exercises_from_exercisedb
from transform import (
    clean_data,
    restore_list_columns,
    transform_data,
    validate_data,
    transform_exercises_from_exercisedb,
    transform_foods_from_csv,
    transform_nutrition_dataset,
    transform_gym_members_to_utilisateurs,
    transform_gym_members_to_mesures,
    transform_diet_reco_to_utilisateurs,
)
from load import SupabaseLoader

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_etl_pipeline():
    """
    Pipeline ETL principal.
    Sources intégrées :
      1. ExerciseDB API          → exercices
      2. Daily Food & Nutrition  → aliments
      3. Gym Members Exercise    → utilisateurs + mesures_biometriques
      4. Diet Recommendations    → utilisateurs
    """
    try:
        logger.info("=" * 60)
        logger.info("Démarrage du pipeline ETL...")
        logger.info("=" * 60)

        loader = SupabaseLoader()
        data_dir = os.path.join(os.path.dirname(__file__), "data")

        # ============================================================
        # 1. EXERCICES — ExerciseDB API (GitHub public mirror)
        # ============================================================
        try:
            logger.info("\n📥 [1/4] Extraction des exercices (ExerciseDB API)...")
            df_exercises = extract_exercises_from_exercisedb(limit=200)
            df_exercises = transform_exercises_from_exercisedb(df_exercises)
            df_exercises = clean_data(df_exercises)

            if validate_data(df_exercises, ['nom']):
                logger.info("💾 Chargement des exercices dans Supabase...")
                ok = loader.upsert_dataframe(df_exercises, "exercices", on_conflict="nom")
                logger.info(f"{'✅' if ok else '⚠️ '} {len(df_exercises)} exercices traités")
            else:
                logger.error("❌ Validation échouée pour les exercices")
        except Exception as e:
            logger.error(f"❌ Erreur exercices : {str(e)}", exc_info=True)

        # ============================================================
        # 2. ALIMENTS — Daily Food & Nutrition Dataset (Kaggle)
        # ============================================================
        try:
            nutrition_path = os.path.join(data_dir, "daily_food_nutrition_dataset.csv")
            logger.info("\n📥 [2/4] Extraction aliments (Daily Food & Nutrition Dataset)...")
            df_nutrition = extract_from_csv(nutrition_path)
            df_aliments = transform_nutrition_dataset(df_nutrition)
            df_aliments = clean_data(df_aliments)

            if validate_data(df_aliments, ['nom', 'calories']):
                logger.info("💾 Chargement des aliments dans Supabase...")
                ok = loader.upsert_dataframe(df_aliments, "aliments", on_conflict="nom")
                logger.info(f"{'✅' if ok else '⚠️ '} {len(df_aliments)} aliments traités")
            else:
                logger.error("❌ Validation échouée pour les aliments")
        except Exception as e:
            logger.error(f"❌ Erreur aliments : {str(e)}", exc_info=True)

        # ============================================================
        # 3. UTILISATEURS + MESURES — Gym Members Exercise Dataset (Kaggle)
        # ============================================================
        try:
            gym_path = os.path.join(data_dir, "gym_members_exercise_tracking.csv")
            logger.info("\n📥 [3/4] Extraction utilisateurs (Gym Members Exercise Dataset)...")
            df_gym = extract_from_csv(gym_path)

            # 3a. Utilisateurs
            df_gym_users = transform_gym_members_to_utilisateurs(df_gym)
            df_gym_users = clean_data(df_gym_users)
            df_gym_users = restore_list_columns(df_gym_users, ['objectifs'])

            if validate_data(df_gym_users, ['email']):
                logger.info("💾 Chargement des utilisateurs gym dans Supabase...")
                ok = loader.upsert_dataframe(df_gym_users, "utilisateurs", on_conflict="email")
                logger.info(f"{'✅' if ok else '⚠️ '} {len(df_gym_users)} utilisateurs gym traités")
            else:
                logger.error("❌ Validation échouée pour les utilisateurs gym")

            # 3b. Mesures biométriques — récupérer les UUIDs insérés
            logger.info("🔗 Récupération des UUIDs pour les mesures biométriques...")
            gym_emails = list(df_gym_users['email'].dropna().unique())
            email_to_id = {}

            # Requêter par batch de 100 (limite Supabase)
            for i in range(0, len(gym_emails), 100):
                batch = gym_emails[i:i + 100]
                res = loader.client.table("utilisateurs").select("id_utilisateur,email").in_("email", batch).execute()
                for row in res.data:
                    email_to_id[row['email']] = row['id_utilisateur']

            logger.info(f"   {len(email_to_id)}/{len(gym_emails)} utilisateurs retrouvés")

            df_mesures = transform_gym_members_to_mesures(df_gym, email_to_id)
            if len(df_mesures) > 0:
                logger.info("💾 Chargement des mesures biométriques dans Supabase...")
                ok = loader.load_dataframe(df_mesures, "mesures_biometriques")
                logger.info(f"{'✅' if ok else '⚠️ '} {len(df_mesures)} mesures biométriques traitées")
        except Exception as e:
            logger.error(f"❌ Erreur gym members : {str(e)}", exc_info=True)

        # ============================================================
        # 4. UTILISATEURS — Diet Recommendations Dataset (Kaggle)
        # ============================================================
        try:
            diet_path = os.path.join(data_dir, "diet_recommendations_dataset.csv")
            logger.info("\n📥 [4/4] Extraction utilisateurs (Diet Recommendations Dataset)...")
            df_diet = extract_from_csv(diet_path)

            df_diet_users = transform_diet_reco_to_utilisateurs(df_diet)
            df_diet_users = clean_data(df_diet_users)
            df_diet_users = restore_list_columns(df_diet_users, ['objectifs'])

            if validate_data(df_diet_users, ['email']):
                logger.info("💾 Chargement des utilisateurs diet dans Supabase...")
                ok = loader.upsert_dataframe(df_diet_users, "utilisateurs", on_conflict="email")
                logger.info(f"{'✅' if ok else '⚠️ '} {len(df_diet_users)} utilisateurs diet traités")
            else:
                logger.error("❌ Validation échouée pour les utilisateurs diet")
        except Exception as e:
            logger.error(f"❌ Erreur diet recommendations : {str(e)}", exc_info=True)

        logger.info("\n" + "=" * 60)
        logger.info("✅ Pipeline ETL terminé avec succès !")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Pipeline ETL échoué : {str(e)}", exc_info=True)
        raise


def main():
    """Main function to start the scheduler"""
    scheduler = BlockingScheduler()
    
    # Get schedule from environment variable (default: every 6 hours)
    schedule = os.getenv("ETL_SCHEDULE", "0 */6 * * *")
    
    # Parse cron schedule (format: "minute hour day month day_of_week")
    # Example: "0 */6 * * *" = every 6 hours
    try:
        parts = schedule.split()
        if len(parts) == 5:
            minute, hour, day, month, day_of_week = parts
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            )
        else:
            # Default: every 6 hours
            trigger = CronTrigger(hour="*/6")
    except:
        # Default: every 6 hours
        trigger = CronTrigger(hour="*/6")
    
    # Schedule the ETL job
    scheduler.add_job(
        run_etl_pipeline,
        trigger=trigger,
        id='etl_job',
        name='ETL Pipeline',
        replace_existing=True
    )
    
    logger.info(f"ETL scheduler started with schedule: {schedule}")
    logger.info("Press Ctrl+C to exit")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
        scheduler.shutdown()


if __name__ == "__main__":
    import sys
    
    # Si l'argument "run" est passé, exécuter le pipeline une fois
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        logger.info("Running ETL pipeline once (manual execution)...")
        run_etl_pipeline()
    else:
        # Start scheduler
        main()

