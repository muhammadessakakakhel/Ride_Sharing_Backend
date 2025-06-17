from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, ARRAY, Text, Float
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.config.database import Base
import datetime

class PreScheduledTrip(Base):
    __tablename__ = "pre_scheduled_trips"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    departure_tw_start = Column(DateTime, nullable=False)
    departure_tw_end = Column(DateTime, nullable=False)
    return_tw_start = Column(DateTime, nullable=False)
    return_tw_end = Column(DateTime, nullable=False)
    available_seats = Column(Integer, nullable=False)
    status = Column(String, default="SCHEDULED")
    accepts_packages = Column(Boolean, default=False)
    is_accepting_bookings = Column(Boolean, default=True)
    origin_location = Column(Geometry('POINT', srid=4326))
    destination_location = Column(Geometry('POINT', srid=4326))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    driver = relationship("Driver", back_populates="pre_scheduled_trips")
    trip_bookings = relationship("TripBooking", back_populates="trip")
    packages = relationship("Package", back_populates="trip")
    trip_stops = relationship("TripStop", back_populates="trip")

class TripBooking(Base):
    __tablename__ = "trip_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("pre_scheduled_trips.id"))
    ride_request_id = Column(Integer, ForeignKey("ride_requests.id"))
    seats_booked = Column(Integer, nullable=False)
    booking_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="CONFIRMED")
    fare_amount = Column(Float)
    
    # Relationships
    trip = relationship("PreScheduledTrip", back_populates="trip_bookings")
    ride_request = relationship("RideRequest", back_populates="trip_bookings")

class Package(Base):
    __tablename__ = "packages"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("pre_scheduled_trips.id"))
    package_type = Column(String)
    description = Column(Text)
    weight = Column(Float)
    volume = Column(Float)
    pickup_location = Column(Geometry('POINT', srid=4326))
    dropoff_location = Column(Geometry('POINT', srid=4326))
    pickup_tw_start = Column(DateTime)
    pickup_tw_end = Column(DateTime)
    dropoff_tw_start = Column(DateTime)
    dropoff_tw_end = Column(DateTime)
    status = Column(String, default="PENDING")
    
    # Relationships
    trip = relationship("PreScheduledTrip", back_populates="packages")

class TripStop(Base):
    __tablename__ = "trip_stops"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("pre_scheduled_trips.id"), nullable=True)
    solo_trip_id = Column(Integer, ForeignKey("solo_trips.id"), nullable=True)
    location = Column(Geometry('POINT', srid=4326))
    stop_order = Column(Integer, nullable=False)
    planned_arrival_time = Column(DateTime)
    planned_departure_time = Column(DateTime)
    stop_type = Column(String, nullable=False)
    address = Column(Text)
    notes = Column(Text)
    
    # Relationships
    trip = relationship("PreScheduledTrip", back_populates="trip_stops")
