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
    transform_data, 
    validate_data,
    transform_exercises_from_exercisedb,
    transform_foods_from_csv
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
    Main ETL pipeline function
    Extracts data from various sources, transforms it, and loads into Supabase
    """
    try:
        logger.info("=" * 60)
        logger.info("Starting ETL pipeline...")
        logger.info("=" * 60)
        
        # Initialize loader
        loader = SupabaseLoader()
        
        # ============================================
        # 1. EXTRACT & LOAD EXERCISES FROM EXERCISEDB
        # ============================================
        try:
            logger.info("\n📥 Extracting exercises from ExerciseDB API...")
            df_exercises = extract_exercises_from_exercisedb(limit=200)  # Limiter à 200 exercices
            
            logger.info("🔄 Transforming exercises data...")
            df_exercises = transform_exercises_from_exercisedb(df_exercises)
            df_exercises = clean_data(df_exercises)
            
            # Valider les colonnes requises (certaines sont optionnelles)
            required_cols = ['nom']  # Seul le nom est vraiment requis
            if validate_data(df_exercises, required_cols):
                logger.info("💾 Loading exercises into Supabase...")
                # Utiliser upsert pour éviter les doublons
                success = loader.upsert_dataframe(
                    df_exercises, 
                    table_name="exercices",
                    on_conflict="nom"  # Éviter les doublons par nom
                )
                if success:
                    logger.info(f"✅ Successfully loaded {len(df_exercises)} exercises")
                else:
                    logger.warning("⚠️  Failed to load some exercises")
            else:
                logger.error("❌ Exercise data validation failed")
        except Exception as e:
            logger.error(f"❌ Error processing exercises: {str(e)}", exc_info=True)
        
        # ============================================
        # 2. EXTRACT & LOAD FOODS FROM CSV (if available)
        # ============================================
        try:
            # Chercher des fichiers CSV dans le dossier data
            data_dir = os.path.join(os.path.dirname(__file__), "data")
            csv_files = [f for f in os.listdir(data_dir) if f.endswith(('.csv', '.CSV'))] if os.path.exists(data_dir) else []
            
            if csv_files:
                logger.info(f"\n📥 Found {len(csv_files)} CSV file(s) in data/ directory")
                for csv_file in csv_files:
                    csv_path = os.path.join(data_dir, csv_file)
                    logger.info(f"📥 Extracting foods from {csv_file}...")
                    
                    df_foods = extract_from_csv(csv_path)
                    
                    logger.info("🔄 Transforming foods data...")
                    df_foods = transform_foods_from_csv(df_foods)
                    df_foods = clean_data(df_foods)
                    
                    # Valider les colonnes requises
                    required_cols = ['nom', 'calories']
                    if validate_data(df_foods, required_cols):
                        logger.info("💾 Loading foods into Supabase...")
                        success = loader.upsert_dataframe(
                            df_foods,
                            table_name="aliments",
                            on_conflict="nom"  # Éviter les doublons par nom
                        )
                        if success:
                            logger.info(f"✅ Successfully loaded {len(df_foods)} foods from {csv_file}")
                        else:
                            logger.warning(f"⚠️  Failed to load some foods from {csv_file}")
                    else:
                        logger.error(f"❌ Food data validation failed for {csv_file}")
            else:
                logger.info("\nℹ️  No CSV files found in data/ directory")
                logger.info("   You can add nutrition datasets (CSV) to etl/data/ to load them")
        except Exception as e:
            logger.error(f"❌ Error processing foods: {str(e)}", exc_info=True)
        
        # ============================================
        # 3. CREATE SAMPLE USERS (for testing)
        # ============================================
        try:
            logger.info("\n👥 Creating sample users...")
            import uuid
            from datetime import datetime
            
            sample_users = [
                {
                    "email": f"user1-{uuid.uuid4().hex[:8]}@example.com",
                    "nom": "Dupont",
                    "prenom": "Jean",
                    "age": 28,
                    "sexe": "M",
                    "poids": 75.0,
                    "taille": 180.0,
                    "type_abonnement": "premium",
                    "objectifs": ["perte de poids", "musculation"]
                },
                {
                    "email": f"user2-{uuid.uuid4().hex[:8]}@example.com",
                    "nom": "Martin",
                    "prenom": "Marie",
                    "age": 32,
                    "sexe": "F",
                    "poids": 65.0,
                    "taille": 165.0,
                    "type_abonnement": "freemium",
                    "objectifs": ["forme", "cardio"]
                }
            ]
            
            df_users = pd.DataFrame(sample_users)
            # Convertir objectifs en liste Python (Supabase gère les arrays PostgreSQL)
            # On garde comme liste, Supabase le convertira automatiquement
            
            # Vérifier si les utilisateurs existent déjà (par email)
            success = loader.upsert_dataframe(
                df_users,
                table_name="utilisateurs",
                on_conflict="email"  # Utiliser email comme clé unique
            )
            if success:
                logger.info(f"✅ Created/updated {len(sample_users)} sample users")
        except Exception as e:
            logger.error(f"❌ Error creating sample users: {str(e)}", exc_info=True)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ ETL pipeline completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ ETL pipeline failed: {str(e)}", exc_info=True)
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

