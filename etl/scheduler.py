"""
ETL Scheduler
Schedule and run ETL jobs
"""
import os
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from extract import extract_from_csv, extract_from_excel, extract_from_api
from transform import clean_data, transform_data, validate_data
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
    Customize this function according to your data sources and transformations
    """
    try:
        logger.info("Starting ETL pipeline...")
        
        # Initialize loader
        loader = SupabaseLoader()
        
        # Example ETL process:
        # 1. Extract
        # df = extract_from_csv("data/example.csv")
        # or
        # df = extract_from_api("https://api.example.com/data")
        
        # 2. Transform
        # df = clean_data(df)
        # df = transform_data(df)
        
        # 3. Validate
        # required_columns = ["id", "name", "date"]
        # if not validate_data(df, required_columns):
        #     raise ValueError("Data validation failed")
        
        # 4. Load
        # loader.load_dataframe(df, "table_name")
        
        logger.info("ETL pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}", exc_info=True)


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
    # Run once immediately for testing
    # run_etl_pipeline()
    
    # Start scheduler
    main()

