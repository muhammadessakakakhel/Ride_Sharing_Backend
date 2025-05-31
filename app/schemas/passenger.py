from pydantic import BaseModel, EmailStr
from typing import Optional

class PassengerBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    gender: Optional[str] = None
    prefer_same_gender_driver: Optional[bool] = False
    prefer_same_gender_pool: Optional[bool] = False

class PassengerCreate(PassengerBase):
    pass

class PassengerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    prefer_same_gender_driver: Optional[bool] = None
    prefer_same_gender_pool: Optional[bool] = None

class PassengerResponse(PassengerBase):
    id: int
    
    class Config:
        from_attributes = True