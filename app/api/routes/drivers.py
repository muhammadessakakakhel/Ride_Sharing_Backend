from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.models.driver import Driver, CurrentDriverLocation
from app.schemas.driver import (
    DriverResponse, DriverCreate, DriverUpdate, DriverCreateResponse,
    DriverUpdateResponse, DriverDeleteResponse, DriverLocationUpdate, DriverLocationResponse
)
from app.services.driver_service import DriverService

router = APIRouter()

# ==================== READ OPERATIONS ====================

@router.get("/", response_model=List[DriverResponse])
async def get_all_drivers(db: Session = Depends(get_db)):
    """
    Get all drivers
    
    Returns a list of all drivers in the system.
    """
    drivers = DriverService.get_all_drivers(db)
    return drivers

@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(driver_id: int, db: Session = Depends(get_db)):
    """
    Get driver by ID
    
    Returns detailed information about a specific driver.
    """
    driver = DriverService.get_driver_by_id(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

# ==================== CREATE OPERATION ====================

@router.post("/", response_model=DriverCreateResponse, status_code=201)
async def create_driver(
    driver_data: DriverCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new driver
    
    Creates a new driver in the system with the provided information.
    
    **Business Rules:**
    - Vehicle must exist and not be assigned to another driver
    - Email must be unique
    - All required fields must be provided
    
    **Example:**
    ```json
    {
        "vehicle_id": 1,
        "name": "Ahmad Ali",
        "email": "ahmad@example.com",
        "phone_number": "0777111222",
        "gender": "male"
    }
    ```
    """
    try:
        new_driver = DriverService.create_driver(db, driver_data)
        return DriverCreateResponse(
            id=new_driver.id,
            vehicle_id=new_driver.vehicle_id,
            name=new_driver.name,
            email=new_driver.email,
            phone_number=new_driver.phone_number,
            gender=new_driver.gender,
            message="Driver created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ==================== UPDATE OPERATION ====================

@router.put("/{driver_id}", response_model=DriverUpdateResponse)
async def update_driver(
    driver_id: int,
    driver_data: DriverUpdate,
    db: Session = Depends(get_db)
):
    """
    Update driver information
    
    Updates existing driver information. Only provided fields will be updated.
    
    **Business Rules:**
    - Driver must exist
    - If email is changed, it must be unique
    - Partial updates are supported (only provide fields you want to change)
    
    **Example:**
    ```json
    {
        "name": "Updated Name",
        "phone_number": "0777999888"
    }
    ```
    """
    try:
        updated_driver = DriverService.update_driver(db, driver_id, driver_data)
        return DriverUpdateResponse(
            id=updated_driver.id,
            vehicle_id=updated_driver.vehicle_id,
            name=updated_driver.name,
            email=updated_driver.email,
            phone_number=updated_driver.phone_number,
            gender=updated_driver.gender,
            message="Driver updated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ==================== DELETE OPERATION ====================

@router.delete("/{driver_id}", response_model=DriverDeleteResponse)
async def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    """
    Delete a driver
    
    Permanently removes a driver from the system.
    
    **Warning:** This action cannot be undone.
    
    **Business Rules:**
    - Driver must exist
    - Associated location data will be removed
    """
    try:
        result = DriverService.delete_driver(db, driver_id)
        return DriverDeleteResponse(
            message=result["message"],
            deleted_driver_id=result["deleted_driver_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ==================== LOCATION OPERATIONS (Your Existing Logic) ====================

@router.put("/{driver_id}/location")
async def update_driver_location(
    driver_id: int,
    location_update: DriverLocationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update driver's current location
    
    Updates the real-time location of a driver for matching purposes.
    """
    try:
        result = DriverService.update_driver_location(
            db=db,
            driver_id=driver_id,
            latitude=location_update.latitude,
            longitude=location_update.longitude,
            heading=location_update.heading,
            location_source=location_update.location_source
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{driver_id}/location")
async def get_driver_location(driver_id: int, db: Session = Depends(get_db)):
    """
    Get driver's current location
    
    Returns the latest GPS location of the specified driver.
    """
    try:
        location = DriverService.get_driver_location(db, driver_id)
        if not location:
            raise HTTPException(status_code=404, detail="Driver location not found")
        return location
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")