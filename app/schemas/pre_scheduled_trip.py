from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# Import the FeaturePreferences from ride_request to maintain consistency
from app.schemas.ride_request import FeaturePreferences

class PreScheduledTripMatchRequest(BaseModel):
    pickup_latitude: float = Field(..., description="Pickup latitude")
    pickup_longitude: float = Field(..., description="Pickup longitude")
    dropoff_latitude: float = Field(..., description="Dropoff latitude")
    dropoff_longitude: float = Field(..., description="Dropoff longitude")
    pickup_tw_start: datetime = Field(..., description="Pickup time window start")
    pickup_tw_end: datetime = Field(..., description="Pickup time window end")
    seats_required: Optional[int] = Field(1, ge=1, le=8, description="Number of seats required")
    wheelchair_needed: Optional[bool] = Field(False, description="Wheelchair accessibility needed")
    
    # FIXED: Use the same FeaturePreferences class as direct matching
    feature_preferences: Optional[FeaturePreferences] = Field(
        None,
        description="Vehicle feature preferences with required and optional lists",
        example={
            "required": ["AC"],
            "optional": ["USB_Charger", "WiFi"]
        }
    )
    
    max_results: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results")
    max_pickup_distance_meters: Optional[int] = Field(2000, ge=100, le=50000, description="Maximum pickup distance in meters")
    max_dropoff_distance_meters: Optional[int] = Field(2000, ge=100, le=50000, description="Maximum dropoff distance in meters")
    max_time_window_minutes: Optional[int] = Field(120, ge=1, le=1440, description="Maximum time window in minutes")

class PreScheduledTripMatchResponse(BaseModel):
    trip_id: int
    driver_id: int
    driver_name: str
    driver_gender: Optional[str] = None
    vehicle_license_plate: str
    available_seats: int
    departure_tw_start: datetime
    departure_tw_end: datetime
    return_tw_start: datetime
    return_tw_end: datetime
    pickup_distance_meters: float
    dropoff_distance_meters: float
    time_difference_minutes: int
    origin_coordinates: str
    destination_coordinates: str
    has_wheelchair_access: bool
    available_features: List[str]
    accepts_packages: bool
    match_score: float
    distance_score: float
    time_score: float
    feature_score: float
    capacity_utilization: float

class PreScheduledTripCreate(BaseModel):
    driver_id: int
    departure_tw_start: datetime
    departure_tw_end: datetime
    return_tw_start: datetime
    return_tw_end: datetime
    available_seats: int
    accepts_packages: Optional[bool] = False
    origin_latitude: float
    origin_longitude: float
    destination_latitude: float
    destination_longitude: float

class PreScheduledTripResponse(BaseModel):
    id: int
    driver_id: int
    departure_tw_start: datetime
    departure_tw_end: datetime
    return_tw_start: datetime
    return_tw_end: datetime
    available_seats: int
    status: str
    accepts_packages: bool
    is_accepting_bookings: bool
    created_at: datetime
    
    class Config:
        from_attributes = True