"""
FastAPI Backend for ElectronicsHotDeals
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from routes.products import router as products_router
from scheduler import create_scheduler, run_scraping_pipeline, get_scrape_status
from models import ScrapeStatus

# Scheduler instance
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global scheduler
    # Start scheduler on startup
    scheduler = create_scheduler(interval_hours=6)
    scheduler.start()
    print("🚀 Scheduler started - auto-scraping every 6 hours")
    
    yield
    
    # Shutdown scheduler
    if scheduler:
        scheduler.shutdown()
        print("🛑 Scheduler stopped")


app = FastAPI(
    title="ElectronicsHotDeals API",
    description="API for Jumia & Electroplanet electronics deals",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(products_router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "ElectronicsHotDeals API is running"}


@app.get("/api/scrape/status", response_model=ScrapeStatus)
async def scrape_status():
    """Get the current scraping status"""
    status = get_scrape_status()
    
    # Get product count from data file
    data_file = Path(__file__).parent.parent / "jumia_products_clean.csv"
    products_count = 0
    if data_file.exists():
        import pandas as pd
        try:
            df = pd.read_csv(data_file)
            products_count = len(df)
        except:
            pass
    
    return ScrapeStatus(
        last_scrape=status.get("last_scrape"),
        status=status.get("status", "unknown"),
        products_count=products_count,
        is_running=status.get("is_running", False),
    )


@app.post("/api/scrape/trigger")
async def trigger_scrape(background_tasks: BackgroundTasks):
    """Manually trigger a scrape"""
    status = get_scrape_status()
    
    if status.get("is_running"):
        return {"success": False, "message": "Scraping already in progress"}
    
    background_tasks.add_task(run_scraping_pipeline)
    return {"success": True, "message": "Scraping started in background"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
