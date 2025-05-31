# app/schemas/ride_request.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class FeaturePreferences(BaseModel):
    """Feature preferences with required and optional features"""
    required: Optional[List[str]] = Field(default=[], description="Required vehicle features")
    optional: Optional[List[str]] = Field(default=[], description="Optional vehicle features")

class RideRequestBase(BaseModel):
    pickup_latitude: float = Field(..., description="Pickup latitude")
    pickup_longitude: float = Field(..., description="Pickup longitude")
    dropoff_latitude: float = Field(..., description="Dropoff latitude")
    dropoff_longitude: float = Field(..., description="Dropoff longitude")
    pickup_tw_start: datetime = Field(..., description="Pickup time window start")
    pickup_tw_end: datetime = Field(..., description="Pickup time window end")
    dropoff_tw_start: Optional[datetime] = Field(None, description="Dropoff time window start")
    dropoff_tw_end: Optional[datetime] = Field(None, description="Dropoff time window end")
    wheelchair_needed: Optional[bool] = Field(False, description="Wheelchair accessibility needed")
    seats_required: Optional[int] = Field(1, ge=1, le=8, description="Number of seats required")
    feature_preferences: Optional[FeaturePreferences] = Field(None, description="Vehicle feature preferences")

class RideRequestCreate(RideRequestBase):
    passenger_id: int

class RideRequestResponse(RideRequestBase):
    id: int
    passenger_id: int
    requested_time: datetime
    status: str
    assigned_driver_id: Optional[int] = None
    estimated_distance: Optional[float] = None
    estimated_duration: Optional[float] = None
    estimated_fare: Optional[float] = None
    
    class Config:
        from_attributes = True

class DriverMatchRequest(BaseModel):
    pickup_latitude: float = Field(..., description="Pickup latitude")
    pickup_longitude: float = Field(..., description="Pickup longitude")
    dropoff_latitude: float = Field(..., description="Dropoff latitude")
    dropoff_longitude: float = Field(..., description="Dropoff longitude")
    pickup_tw_start: datetime = Field(..., description="Pickup time window start")
    pickup_tw_end: datetime = Field(..., description="Pickup time window end")
    seats_required: Optional[int] = Field(1, ge=1, le=8, description="Number of seats required")
    wheelchair_needed: Optional[bool] = Field(False, description="Wheelchair accessibility needed")
    
    # CORRECTED: Now matches your PostgreSQL JSONB structure
    feature_preferences: Optional[FeaturePreferences] = Field(
        None, 
        description="Vehicle feature preferences with required and optional lists",
        example={
            "required": ["AC"],
            "optional": ["USB_Charger", "WiFi"]
        }
    )
    
    max_results: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results")
    max_distance_meters: Optional[int] = Field(5000, ge=100, le=50000, description="Maximum distance in meters")
    max_waiting_minutes: Optional[int] = Field(30, ge=1, le=120, description="Maximum waiting time in minutes")

class DriverMatchResponse(BaseModel):
    driver_id: int
    driver_name: str
    vehicle_id: int
    distance_to_pickup: float
    estimated_arrival_time: datetime
    travel_time_minutes: float
    seat_capacity: int
    has_wheelchair_access: bool
    available_features: List[str]
    match_score: float
    proximity_score: float
    temporal_score: float
    vehicle_score: float
    feature_score: float
    estimated_fare: float