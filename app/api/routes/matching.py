from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.schemas.ride_request import DriverMatchRequest, DriverMatchResponse
from app.services.driver_matching import DriverMatchingService

router = APIRouter()

@router.post("/find-drivers", response_model=List[DriverMatchResponse])
async def find_matching_drivers(
    request: DriverMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Find matching drivers for a ride request based on location, time windows, and preferences.
    
    This endpoint uses the sophisticated PostgreSQL matching algorithm to find the best 
    available drivers considering:
    - Proximity to pickup location
    - Availability within time windows
    - Vehicle capacity and accessibility requirements
    - Feature preferences
    - Overall match scoring
    """
    try:
        print("This is request:",request)
        matches = DriverMatchingService.find_matching_drivers(db, request)
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding matching drivers: {str(e)}")

@router.get("/test-matching")
async def test_matching_endpoint(db: Session = Depends(get_db)):
    """
    Test endpoint with predefined parameters to verify the matching algorithm
    """
    from datetime import datetime, timedelta
    
    test_request = DriverMatchRequest(
        pickup_latitude=31.9450,
        pickup_longitude=35.9150,
        dropoff_latitude=31.9800,
        dropoff_longitude=35.8800,
        pickup_tw_start=datetime.now() + timedelta(minutes=10),
        pickup_tw_end=datetime.now() + timedelta(minutes=25),
        seats_required=2,
        wheelchair_needed=False,
        feature_preferences={"required": ["AC"], "optional": ["USB_Charger", "WiFi"]},
        max_results=10,
        max_distance_meters=5000,
        max_waiting_minutes=30
    )
    
    try:
        matches = DriverMatchingService.find_matching_drivers(db, test_request)
        return {
            "message": "Test successful",
            "request_parameters": test_request.dict(),
            "matches_found": len(matches),
            "matches": matches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")