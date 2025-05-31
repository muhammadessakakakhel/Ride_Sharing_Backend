from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import JSON
from geoalchemy2 import Geometry
from app.config.database import Base
import datetime

class RideRequest(Base):
    __tablename__ = "ride_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"))
    pickup_location = Column(Geometry('POINT', srid=4326))
    dropoff_location = Column(Geometry('POINT', srid=4326))
    requested_time = Column(DateTime, default=datetime.datetime.utcnow)
    pickup_tw_start = Column(DateTime)
    pickup_tw_end = Column(DateTime)
    dropoff_tw_start = Column(DateTime)
    dropoff_tw_end = Column(DateTime)
    wheelchair_needed = Column(Boolean, default=False)
    seats_required = Column(Integer, default=1)
    status = Column(String, default="PENDING")
    assigned_driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    estimated_distance = Column(Float)
    estimated_duration = Column(Float)
    estimated_fare = Column(Float)
    feature_preferences = Column(JSON)