from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import engine, Base
from app.api.routes import drivers, passengers, rides, matching
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ride Sharing API",
    description="A comprehensive ride-sharing platform with advanced driver matching algorithms",
    version="1.0.0",
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
app.include_router(matching.router, prefix="/api/v1/matching", tags=["matching"])

@app.get("/")
async def root():
    return {"message": "Ride Sharing API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ride-sharing-api"}