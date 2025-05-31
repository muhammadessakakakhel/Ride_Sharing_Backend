from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from app.models.driver import Driver, CurrentDriverLocation
from app.models.vehicle import Vehicle
from app.schemas.driver import DriverCreate, DriverUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class DriverService:
    """
    Service layer for driver operations following your existing architecture patterns.
    
    Why Service Layer?
    - Separates business logic from API routes (like your DriverMatchingService)
    - Makes code testable and reusable
    - Centralizes validation and error handling
    - Follows your existing professional patterns
    """
    
    @staticmethod
    def get_all_drivers(db: Session) -> List[Driver]:
        """Get all drivers from database"""
        return db.query(Driver).all()
    
    @staticmethod
    def get_driver_by_id(db: Session, driver_id: int) -> Optional[Driver]:
        """Get driver by ID"""
        return db.query(Driver).filter(Driver.id == driver_id).first()
    
    @staticmethod
    def create_driver(db: Session, driver_data: DriverCreate) -> Driver:
        """
        Create a new driver with validation
        
        Business Rules:
        1. Vehicle must exist
        2. Vehicle cannot be assigned to another driver
        3. Email must be unique
        4. All required fields must be provided
        """
        try:
            # Validation 1: Check if vehicle exists
            vehicle = db.query(Vehicle).filter(Vehicle.id == driver_data.vehicle_id).first()
            if not vehicle:
                raise ValueError(f"Vehicle with ID {driver_data.vehicle_id} not found")
            
            # Validation 2: Check if vehicle is already assigned
            existing_assignment = db.query(Driver).filter(
                Driver.vehicle_id == driver_data.vehicle_id
            ).first()
            if existing_assignment:
                raise ValueError(f"Vehicle {driver_data.vehicle_id} is already assigned to driver: {existing_assignment.name}")
            
            # Validation 3: Check if email is unique
            existing_email = db.query(Driver).filter(Driver.email == driver_data.email).first()
            if existing_email:
                raise ValueError(f"Email {driver_data.email} is already registered")
            
            # Create new driver
            new_driver = Driver(
                vehicle_id=driver_data.vehicle_id,
                name=driver_data.name,
                email=driver_data.email,
                phone_number=driver_data.phone_number,
                gender=driver_data.gender
            )
            
            # Save to database
            db.add(new_driver)
            db.commit()
            db.refresh(new_driver)  # Get the generated ID
            
            logger.info(f"Created new driver: {new_driver.name} (ID: {new_driver.id})")
            return new_driver
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error: {str(e)}")
            raise ValueError("Database constraint violation")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating driver: {str(e)}")
            raise e
    
    @staticmethod
    def update_driver(db: Session, driver_id: int, driver_data: DriverUpdate) -> Driver:
        """
        Update driver information
        
        Business Rules:
        1. Driver must exist
        2. If email is being changed, it must be unique
        3. Only update fields that are provided (partial update)
        """
        try:
            # Get existing driver
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                raise ValueError(f"Driver with ID {driver_id} not found")
            
            # Check email uniqueness if email is being updated
            if driver_data.email and driver_data.email != driver.email:
                existing_email = db.query(Driver).filter(
                    Driver.email == driver_data.email,
                    Driver.id != driver_id
                ).first()
                if existing_email:
                    raise ValueError(f"Email {driver_data.email} is already registered")
            
            # Update only provided fields (partial update)
            update_data = driver_data.dict(exclude_unset=True)  # Only fields that were provided
            for field, value in update_data.items():
                setattr(driver, field, value)
            
            db.commit()
            db.refresh(driver)
            
            logger.info(f"Updated driver: {driver.name} (ID: {driver.id})")
            return driver
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating driver {driver_id}: {str(e)}")
            raise e
    
    @staticmethod
    def delete_driver(db: Session, driver_id: int) -> dict:
        """
        Delete driver (soft delete approach)
        
        Business Rules:
        1. Driver must exist
        2. Remove driver location data when deleting
        3. Return confirmation message
        """
        try:
            # Get existing driver
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                raise ValueError(f"Driver with ID {driver_id} not found")
            
            driver_name = driver.name  # Store name for response
            
            # Delete associated location data first (foreign key constraint)
            db.query(CurrentDriverLocation).filter(
                CurrentDriverLocation.driver_id == driver_id
            ).delete()
            
            # Delete the driver
            db.delete(driver)
            db.commit()
            
            logger.info(f"Deleted driver: {driver_name} (ID: {driver_id})")
            return {
                "message": f"Driver {driver_name} deleted successfully",
                "deleted_driver_id": driver_id
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting driver {driver_id}: {str(e)}")
            raise e
    
    @staticmethod
    def update_driver_location(
        db: Session, 
        driver_id: int, 
        latitude: float, 
        longitude: float, 
        heading: Optional[float] = None,
        location_source: str = "GPS"
    ) -> dict:
        """
        Update driver's current location (keeping your existing logic)
        
        Why in Service Layer?
        - Complex geospatial logic
        - Business rule: driver must exist
        - Reusable across different endpoints
        """
        try:
            # Check if driver exists
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                raise ValueError(f"Driver with ID {driver_id} not found")
            
            # Check if location record exists
            current_location = db.query(CurrentDriverLocation).filter(
                CurrentDriverLocation.driver_id == driver_id
            ).first()
            
            if current_location:
                # Update existing location
                db.execute(
                    text("""
                        UPDATE current_driver_locations 
                        SET location = ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                            updated_at = NOW(),
                            heading = :heading,
                            location_source = :location_source
                        WHERE driver_id = :driver_id
                    """),
                    {
                        "lon": longitude,
                        "lat": latitude,
                        "heading": heading,
                        "location_source": location_source,
                        "driver_id": driver_id
                    }
                )
            else:
                # Create new location record
                db.execute(
                    text("""
                        INSERT INTO current_driver_locations (driver_id, location, updated_at, heading, location_source)
                        VALUES (:driver_id, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), NOW(), :heading, :location_source)
                    """),
                    {
                        "driver_id": driver_id,
                        "lon": longitude,
                        "lat": latitude,
                        "heading": heading,
                        "location_source": location_source
                    }
                )
            
            db.commit()
            return {"message": "Location updated successfully"}
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating location for driver {driver_id}: {str(e)}")
            raise e
    
    @staticmethod
    def get_driver_location(db: Session, driver_id: int) -> Optional[dict]:
        """Get driver's current location (keeping your existing logic)"""
        try:
            # Check if driver exists
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                raise ValueError(f"Driver with ID {driver_id} not found")
            
            result = db.execute(
                text("""
                    SELECT 
                        driver_id,
                        ST_X(location) as longitude,
                        ST_Y(location) as latitude,
                        updated_at,
                        heading,
                        location_source
                    FROM current_driver_locations 
                    WHERE driver_id = :driver_id
                """),
                {"driver_id": driver_id}
            ).first()
            
            if not result:
                return None
            
            return {
                "driver_id": result.driver_id,
                "latitude": result.latitude,
                "longitude": result.longitude,
                "updated_at": result.updated_at,
                "heading": result.heading,
                "location_source": result.location_source
            }
            
        except Exception as e:
            logger.error(f"Error getting location for driver {driver_id}: {str(e)}")
            raise e