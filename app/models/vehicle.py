from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from app.config.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_type_id = Column(Integer, ForeignKey("vehicle_types.id"))
    license_plate = Column(String, unique=True, nullable=False)
    color = Column(String)
    is_active = Column(Boolean, default=True)
    seat_capacity = Column(Integer, nullable=False)
    has_wheelchair_access = Column(Boolean, default=False)
    available_features = Column(ARRAY(String))
    
    # Relationships
    driver = relationship("Driver", back_populates="vehicle", uselist=False)
    vehicle_type = relationship("VehicleType", back_populates="vehicles")

class VehicleType(Base):
    __tablename__ = "vehicle_types"
    
    id = Column(Integer, primary_key=True, index=True)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    body_style = Column(String)
    trim = Column(String)
    transmission = Column(String)
    features = Column(ARRAY(String))
    ride_class = Column(ARRAY(String))
    number_rows = Column(Integer)
    standard_seat_capacity = Column(Integer)
    year = Column(Integer)
    
    # Relationships
    vehicles = relationship("Vehicle", back_populates="vehicle_type")