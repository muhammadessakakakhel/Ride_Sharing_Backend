from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class DriverBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    gender: Optional[str] = None

class DriverCreate(DriverBase):
    vehicle_id: int

class DriverUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None

class DriverResponse(DriverBase):
    id: int
    vehicle_id: int
    
    class Config:
        from_attributes = True

class DriverLocationUpdate(BaseModel):
    latitude: float
    longitude: float
    heading: Optional[float] = None
    location_source: Optional[str] = "GPS"

class DriverLocationResponse(BaseModel):
    driver_id: int
    latitude: float
    longitude: float
    updated_at: datetime
    heading: Optional[float] = None
    location_source: Optional[str] = None
    
    class Config:
        from_attributes = True


    # ADD THESE NEW SCHEMAS TO YOUR EXISTING SCHEMAS FILE:

class DriverCreateResponse(BaseModel):
    """Response schema for driver creation"""
    id: int
    vehicle_id: int
    name: str
    email: str
    phone_number: str
    gender: Optional[str] = None
    message: str = "Driver created successfully"
    
    class Config:
        from_attributes = True

class DriverUpdateResponse(BaseModel):
    """Response schema for driver update"""
    id: int
    vehicle_id: int
    name: str
    email: str
    phone_number: str
    gender: Optional[str] = None
    message: str = "Driver updated successfully"
    
    class Config:
        from_attributes = True

class DriverDeleteResponse(BaseModel):
    """Response schema for driver deletion"""
    message: str
    deleted_driver_id: int