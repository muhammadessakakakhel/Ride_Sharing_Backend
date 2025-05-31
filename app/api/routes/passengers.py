from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.models.passenger import Passenger
from app.schemas.passenger import PassengerResponse

router = APIRouter()

@router.get("/", response_model=List[PassengerResponse])
async def get_all_passengers(db: Session = Depends(get_db)):
    """Get all passengers"""
    passengers = db.query(Passenger).all()
    return passengers

@router.get("/{passenger_id}", response_model=PassengerResponse)
async def get_passenger(passenger_id: int, db: Session = Depends(get_db)):
    """Get passenger by ID"""
    passenger = db.query(Passenger).filter(Passenger.id == passenger_id).first()
    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")
    return passenger