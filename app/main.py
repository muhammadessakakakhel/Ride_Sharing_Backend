from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import engine, Base
from app.api.routes import drivers, passengers, rides, matching, prescheduled_trips, combined_matching
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ride Sharing API",
    description="A comprehensive ride-sharing platform with advanced driver matching and pre-scheduled trip algorithms",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(drivers.router, prefix="/api/v1/drivers", tags=["drivers"])
app.include_router(passengers.router, prefix="/api/v1/passengers", tags=["passengers"])
app.include_router(rides.router, prefix="/api/v1/rides", tags=["rides"])
app.include_router(matching.router, prefix="/api/v1/matching", tags=["direct-matching"])
app.include_router(prescheduled_trips.router, prefix="/api/v1/prescheduled-trips", tags=["prescheduled-trips"])
app.include_router(combined_matching.router, prefix="/api/v1/combined", tags=["combined-matching"])

@app.get("/")
async def root():
    return {
        "message": "Advanced Ride Sharing API is running!", 
        "version": "2.0.0",
        "algorithms": [
            "Direct Driver Matching",
            "Pre-Scheduled Trip Matching",
            "Combined Matching (Both)"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ride-sharing-api"}

@app.get("/algorithms")
async def get_available_algorithms():
    """Get information about available matching algorithms"""
    return {
        "algorithms": [
            {
                "name": "Direct Driver Matching",
                "endpoint": "/api/v1/matching/find-drivers",
                "description": "Find available drivers for immediate ride requests",
                "use_case": "On-demand rides, immediate pickup",
                "parameters": ["pickup/dropoff locations", "time windows", "vehicle requirements"]
            },
            {
                "name": "Pre-Scheduled Trip Matching", 
                "endpoint": "/api/v1/prescheduled-trips/find-trips",
                "description": "Find existing scheduled trips that passengers can join",
                "use_case": "Shared rides, scheduled trips, carpooling",
                "parameters": ["pickup/dropoff locations", "time windows", "distance thresholds"]
            },
            {
                "name": "Combined Matching",
                "endpoint": "/api/v1/combined/find-all-options", 
                "description": "Find both direct drivers and pre-scheduled trips with recommendations",
                "use_case": "Comprehensive ride search with multiple options",
                "parameters": ["all above parameters", "max results per type"]
            }
        ]
    }