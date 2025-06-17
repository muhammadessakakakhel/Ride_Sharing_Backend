from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.config.database import get_db
from app.services.ride_service import CombinedRideService

router = APIRouter()

@router.post("/find-all-options")
async def find_all_ride_options(
    pickup_latitude: float,
    pickup_longitude: float,
    dropoff_latitude: float,
    dropoff_longitude: float,
    pickup_tw_start: datetime,
    pickup_tw_end: datetime,
    seats_required: Optional[int] = 1,
    wheelchair_needed: Optional[bool] = False,
    feature_preferences: Optional[Dict[str, Any]] = None,
    max_results_per_type: Optional[int] = 5,
    db: Session = Depends(get_db)
):
    """
    Find all available ride options including both direct drivers and pre-scheduled trips.
    
    This comprehensive endpoint searches for:
    1. Direct drivers available for immediate pickup
    2. Pre-scheduled trips that the passenger can join
    
    Returns both options with recommendations on the best choice.
    """
    try:
        result = CombinedRideService.find_all_ride_options(
            db=db,
            pickup_latitude=pickup_latitude,
            pickup_longitude=pickup_longitude,
            dropoff_latitude=dropoff_latitude,
            dropoff_longitude=dropoff_longitude,
            pickup_tw_start=pickup_tw_start,
            pickup_tw_end=pickup_tw_end,
            seats_required=seats_required,
            wheelchair_needed=wheelchair_needed,
            feature_preferences=feature_preferences,
            max_results_per_type=max_results_per_type
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding ride options: {str(e)}")

@router.get("/test-combined-matching")
async def test_combined_matching(db: Session = Depends(get_db)):
    """
    Test endpoint to verify both matching algorithms work together
    """
    try:
        result = CombinedRideService.find_all_ride_options(
            db=db,
            pickup_latitude=31.9450,
            pickup_longitude=35.9150,
            dropoff_latitude=31.9800,
            dropoff_longitude=35.8800,
            pickup_tw_start=datetime.now() + timedelta(minutes=10),
            pickup_tw_end=datetime.now() + timedelta(minutes=30),
            seats_required=2,
            wheelchair_needed=False,
            feature_preferences={"required": ["AC"], "optional": ["USB_Charger", "WiFi"]},
            max_results_per_type=5
        )
        
        return {
            "message": "Combined matching test successful",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")