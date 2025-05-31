from sqlalchemy import Column, Integer, String, Boolean
from app.config.database import Base

class Passenger(Base):
    __tablename__ = "passengers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=False)
    gender = Column(String)
    prefer_same_gender_driver = Column(Boolean, default=False)
    prefer_same_gender_pool = Column(Boolean, default=False)