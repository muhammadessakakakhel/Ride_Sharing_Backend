from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, ARRAY, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.config.database import Base
import datetime

class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=False)
    gender = Column(String)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="driver")
    current_location = relationship("CurrentDriverLocation", back_populates="driver", uselist=False)
    location_history = relationship("DriverLocationHistory", back_populates="driver")

class CurrentDriverLocation(Base):
    __tablename__ = "current_driver_locations"
    
    driver_id = Column(Integer, ForeignKey("drivers.id"), primary_key=True)
    location = Column(Geometry('POINT', srid=4326))
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    heading = Column(Integer)
    location_source = Column(String)
    
    # Relationships
    driver = relationship("Driver", back_populates="current_location")

class DriverLocationHistory(Base):
    __tablename__ = "driver_locations_history"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    location = Column(Geometry('POINT', srid=4326))
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    heading = Column(Integer)
    speed = Column(Integer)
    location_source = Column(String)
    
    # Relationships
    driver = relationship("Driver", back_populates="location_history")