"""
APScheduler configuration for automated scraping
"""
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Scrape status tracking
scrape_status = {
    "last_scrape": None,
    "status": "idle",
    "is_running": False,
}


def run_scraping_pipeline():
    """Execute the full scraping and cleaning pipeline"""
    global scrape_status
    
    if scrape_status["is_running"]:
        logger.warning("Scraping already in progress, skipping...")
        return
    
    scrape_status["is_running"] = True
    scrape_status["status"] = "running"
    
    try:
        logger.info("🚀 Starting automated scraping pipeline...")
        
        # Run Jumia scraper
        logger.info("Scraping Jumia...")
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scraper_jumia_electronics.py")],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        if result.returncode != 0:
            logger.error(f"Jumia scraper failed: {result.stderr}")
        else:
            logger.info("✅ Jumia scraping complete")
        
        # Run data cleaner
        logger.info("Cleaning data...")
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "clean_jumia_data.py")],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            logger.error(f"Data cleaning failed: {result.stderr}")
        else:
            logger.info("✅ Data cleaning complete")
        
        scrape_status["last_scrape"] = datetime.now()
        scrape_status["status"] = "completed"
        logger.info("🎉 Scraping pipeline finished successfully!")
        
    except subprocess.TimeoutExpired:
        logger.error("Scraping timed out")
        scrape_status["status"] = "timeout"
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        scrape_status["status"] = f"error: {str(e)}"
    finally:
        scrape_status["is_running"] = False


def create_scheduler(interval_hours: int = 6) -> BackgroundScheduler:
    """Create and configure the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Add scraping job
    scheduler.add_job(
        run_scraping_pipeline,
        trigger=IntervalTrigger(hours=interval_hours),
        id="scraping_job",
        name="Automated Scraping Pipeline",
        replace_existing=True,
    )
    
    logger.info(f"📅 Scheduler configured to run every {interval_hours} hours")
    return scheduler


def get_scrape_status() -> dict:
    """Get current scrape status"""
    return scrape_status.copy()
