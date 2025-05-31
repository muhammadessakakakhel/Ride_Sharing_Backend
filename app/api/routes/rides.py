from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.models.ride_request import RideRequest
from app.schemas.ride_request import RideRequestResponse

router = APIRouter()

@router.get("/", response_model=List[RideRequestResponse])
async def get_all_ride_requests(db: Session = Depends(get_db)):
    """Get all ride requests"""
    ride_requests = db.query(RideRequest).all()
    return ride_requests

@router.get("/{ride_id}", response_model=RideRequestResponse)
async def get_ride_request(ride_id: int, db: Session = Depends(get_db)):
    """Get ride request by ID"""
    ride_request = db.query(RideRequest).filter(RideRequest.id == ride_id).first()
    if not ride_request:
        raise HTTPException(status_code=404, detail="Ride request not found")
    return ride_request