# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime, timedelta
# from app.config.database import get_db
# from app.schemas.pre_scheduled_trip import (
#     PreScheduledTripMatchRequest, 
#     PreScheduledTripMatchResponse,
#     PreScheduledTripCreate,
#     PreScheduledTripResponse
# )
# from app.services.prescheduled_trip_matching import PreScheduledTripMatchingService
# from app.models.pre_scheduled_trip import PreScheduledTrip
# from sqlalchemy import text

# router = APIRouter()

# @router.post("/find-trips", response_model=List[PreScheduledTripMatchResponse])
# async def find_matching_prescheduled_trips(
#     request: PreScheduledTripMatchRequest,
#     db: Session = Depends(get_db)
# ):
#     """
#     Find matching pre-scheduled trips for a ride request.
    
#     This endpoint finds existing pre-scheduled trips that passengers can join,
#     considering:
#     - Proximity to pickup and dropoff locations
#     - Time window compatibility
#     - Available seats and vehicle features
#     - Wheelchair accessibility requirements
#     - Feature preferences matching
    
#     Returns trips sorted by match score with detailed scoring breakdown.
#     """
#     try:
#         matches = PreScheduledTripMatchingService.find_matching_prescheduled_trips(db, request)
#         return matches
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error finding matching trips: {str(e)}")

# @router.get("/test-prescheduled-matching")
# async def test_prescheduled_matching_endpoint(db: Session = Depends(get_db)):
#     """
#     Test endpoint with predefined parameters to verify the pre-scheduled trip matching algorithm
#     """
#     test_request = PreScheduledTripMatchRequest(
#         pickup_latitude=31.9450,
#         pickup_longitude=35.9150,
#         dropoff_latitude=31.9800,
#         dropoff_longitude=35.8800,
#         pickup_tw_start=datetime.now() + timedelta(hours=18),  # 6 PM today
#         pickup_tw_end=datetime.now() + timedelta(hours=20),    # 8 PM today
#         seats_required=2,
#         wheelchair_needed=False,
#         feature_preferences={"required": ["AC"], "optional": ["USB_Charger", "WiFi"]},
#         max_results=10,
#         max_pickup_distance_meters=15000,
#         max_dropoff_distance_meters=15000,
#         max_time_window_minutes=1440  # 24 hours window
#     )
    
#     try:
#         matches = PreScheduledTripMatchingService.find_matching_prescheduled_trips(db, test_request)
#         return {
#             "message": "Pre-scheduled trip matching test successful",
#             "request_parameters": test_request.dict(),
#             "matches_found": len(matches),
#             "matches": matches
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

# @router.get("/", response_model=List[PreScheduledTripResponse])
# async def get_all_prescheduled_trips(
#     skip: int = 0,
#     limit: int = 100,
#     status: str = None,
#     db: Session = Depends(get_db)
# ):
#     """Get all pre-scheduled trips with optional filtering"""
#     query = db.query(PreScheduledTrip)
    
#     if status:
#         query = query.filter(PreScheduledTrip.status == status)
    
#     trips = query.offset(skip).limit(limit).all()
#     return trips

# @router.get("/{trip_id}", response_model=PreScheduledTripResponse)
# async def get_prescheduled_trip(trip_id: int, db: Session = Depends(get_db)):
#     """Get a specific pre-scheduled trip by ID"""
#     trip = db.query(PreScheduledTrip).filter(PreScheduledTrip.id == trip_id).first()
#     if not trip:
#         raise HTTPException(status_code=404, detail="Pre-scheduled trip not found")
#     return trip

# @router.post("/", response_model=PreScheduledTripResponse)
# async def create_prescheduled_trip(
#     trip_data: PreScheduledTripCreate,
#     db: Session = Depends(get_db)
# ):
#     """Create a new pre-scheduled trip"""
#     try:
#         # Create the trip using raw SQL to handle geometry
#         sql_query = text("""
#             INSERT INTO pre_scheduled_trips (
#                 driver_id, departure_tw_start, departure_tw_end, 
#                 return_tw_start, return_tw_end, available_seats,
#                 accepts_packages, origin_location, destination_location, created_at
#             ) VALUES (
#                 :driver_id, :departure_tw_start, :departure_tw_end,
#                 :return_tw_start, :return_tw_end, :available_seats,
#                 :accepts_packages, 
#                 ST_SetSRID(ST_MakePoint(:origin_lon, :origin_lat), 4326),
#                 ST_SetSRID(ST_MakePoint(:dest_lon, :dest_lat), 4326),
#                 NOW()
#             ) RETURNING id;
#         """)
        
#         result = db.execute(sql_query, {
#             "driver_id": trip_data.driver_id,
#             "departure_tw_start": trip_data.departure_tw_start,
#             "departure_tw_end": trip_data.departure_tw_end,
#             "return_tw_start": trip_data.return_tw_start,
#             "return_tw_end": trip_data.return_tw_end,
#             "available_seats": trip_data.available_seats,
#             "accepts_packages": trip_data.accepts_packages,
#             "origin_lon": trip_data.origin_longitude,
#             "origin_lat": trip_data.origin_latitude,
#             "dest_lon": trip_data.destination_longitude,
#             "dest_lat": trip_data.destination_latitude
#         })
        
#         trip_id = result.fetchone()[0]
#         db.commit()
        
#         # Fetch and return the created trip
#         created_trip = db.query(PreScheduledTrip).filter(PreScheduledTrip.id == trip_id).first()
#         return created_trip
        
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Error creating trip: {str(e)}")


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from datetime import datetime, timedelta
from app.config.database import get_db
from app.schemas.pre_scheduled_trip import (
    PreScheduledTripMatchRequest, 
    PreScheduledTripMatchResponse,
    PreScheduledTripCreate,
    PreScheduledTripResponse
)
from app.services.prescheduled_trip_matching import PreScheduledTripMatchingService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/find-trips", response_model=List[PreScheduledTripMatchResponse])
async def find_matching_prescheduled_trips(
    request: PreScheduledTripMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Find matching pre-scheduled trips for a ride request.
    
    This endpoint finds existing pre-scheduled trips that passengers can join,
    considering:
    - Proximity to pickup and dropoff locations
    - Time window compatibility
    - Available seats and vehicle features
    - Wheelchair accessibility requirements
    - Feature preferences matching
    
    Returns trips sorted by match score with detailed scoring breakdown.
    """
    try:
        matches = PreScheduledTripMatchingService.find_matching_prescheduled_trips(db, request)
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding matching trips: {str(e)}")

@router.get("/test-prescheduled-matching")
async def test_prescheduled_matching_endpoint(db: Session = Depends(get_db)):
    """
    Test endpoint with predefined parameters to verify the pre-scheduled trip matching algorithm
    """
    test_request = PreScheduledTripMatchRequest(
        pickup_latitude=31.9450,
        pickup_longitude=35.9150,
        dropoff_latitude=31.9800,
        dropoff_longitude=35.8800,
        pickup_tw_start=datetime.now() + timedelta(hours=18),  # 6 PM today
        pickup_tw_end=datetime.now() + timedelta(hours=20),    # 8 PM today
        seats_required=2,
        wheelchair_needed=False,
        feature_preferences={"required": ["AC"], "optional": ["USB_Charger", "WiFi"]},
        max_results=10,
        max_pickup_distance_meters=15000,
        max_dropoff_distance_meters=15000,
        max_time_window_minutes=1440  # 24 hours window
    )
    
    try:
        matches = PreScheduledTripMatchingService.find_matching_prescheduled_trips(db, test_request)
        return {
            "message": "Pre-scheduled trip matching test successful",
            "request_parameters": test_request.dict(),
            "matches_found": len(matches),
            "matches": matches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

# ==================== FIXED GET ALL TRIPS ====================
@router.get("/", response_model=List[dict])
async def get_all_prescheduled_trips(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get all pre-scheduled trips with optional filtering"""
    try:
        # Use raw SQL to avoid SQLAlchemy geometry issues
        sql_query = """
            SELECT 
                id,
                driver_id,
                departure_tw_start,
                departure_tw_end,
                return_tw_start,
                return_tw_end,
                available_seats,
                status,
                accepts_packages,
                is_accepting_bookings,
                created_at,
                ST_AsText(origin_location) as origin_coordinates,
                ST_AsText(destination_location) as destination_coordinates
            FROM pre_scheduled_trips
            WHERE ($1::text IS NULL OR status = $1)
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """
        
        result = db.execute(text(sql_query), [status, limit, skip])
        trips = []
        
        for row in result:
            trip_dict = {
                "id": row.id,
                "driver_id": row.driver_id,
                "departure_tw_start": row.departure_tw_start,
                "departure_tw_end": row.departure_tw_end,
                "return_tw_start": row.return_tw_start,
                "return_tw_end": row.return_tw_end,
                "available_seats": row.available_seats,
                "status": row.status,
                "accepts_packages": row.accepts_packages,
                "is_accepting_bookings": row.is_accepting_bookings,
                "created_at": row.created_at,
                "origin_coordinates": row.origin_coordinates,
                "destination_coordinates": row.destination_coordinates
            }
            trips.append(trip_dict)
        
        return trips
        
    except Exception as e:
        logger.error(f"Error getting trips: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving trips: {str(e)}")

# ==================== FIXED GET SPECIFIC TRIP ====================
@router.get("/{trip_id}")
async def get_prescheduled_trip(trip_id: int, db: Session = Depends(get_db)):
    """Get a specific pre-scheduled trip by ID"""
    try:
        sql_query = """
            SELECT 
                pt.id,
                pt.driver_id,
                d.name as driver_name,
                pt.departure_tw_start,
                pt.departure_tw_end,
                pt.return_tw_start,
                pt.return_tw_end,
                pt.available_seats,
                pt.status,
                pt.accepts_packages,
                pt.is_accepting_bookings,
                pt.created_at,
                ST_AsText(pt.origin_location) as origin_coordinates,
                ST_AsText(pt.destination_location) as destination_coordinates
            FROM pre_scheduled_trips pt
            JOIN drivers d ON pt.driver_id = d.id
            WHERE pt.id = $1
        """
        
        result = db.execute(text(sql_query), [trip_id]).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Pre-scheduled trip not found")
        
        trip_dict = {
            "id": result.id,
            "driver_id": result.driver_id,
            "driver_name": result.driver_name,
            "departure_tw_start": result.departure_tw_start,
            "departure_tw_end": result.departure_tw_end,
            "return_tw_start": result.return_tw_start,
            "return_tw_end": result.return_tw_end,
            "available_seats": result.available_seats,
            "status": result.status,
            "accepts_packages": result.accepts_packages,
            "is_accepting_bookings": result.is_accepting_bookings,
            "created_at": result.created_at,
            "origin_coordinates": result.origin_coordinates,
            "destination_coordinates": result.destination_coordinates
        }
        
        return trip_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trip {trip_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving trip: {str(e)}")

# ==================== FIXED CREATE TRIP ====================
@router.post("/")
async def create_prescheduled_trip(
    trip_data: PreScheduledTripCreate,
    db: Session = Depends(get_db)
):
    """Create a new pre-scheduled trip"""
    try:
        # First, check if the driver exists
        driver_check = db.execute(text("SELECT id FROM drivers WHERE id = $1"), [trip_data.driver_id]).first()
        if not driver_check:
            raise HTTPException(status_code=400, detail=f"Driver with ID {trip_data.driver_id} does not exist")
        
        # Validate coordinates
        if not (-90 <= trip_data.origin_latitude <= 90) or not (-180 <= trip_data.origin_longitude <= 180):
            raise HTTPException(status_code=400, detail="Invalid origin coordinates")
        
        if not (-90 <= trip_data.destination_latitude <= 90) or not (-180 <= trip_data.destination_longitude <= 180):
            raise HTTPException(status_code=400, detail="Invalid destination coordinates")
        
        # Create the trip using raw SQL to handle geometry
        sql_query = text("""
            INSERT INTO pre_scheduled_trips (
                driver_id, departure_tw_start, departure_tw_end, 
                return_tw_start, return_tw_end, available_seats,
                accepts_packages, origin_location, destination_location, created_at
            ) VALUES (
                :driver_id, :departure_tw_start, :departure_tw_end,
                :return_tw_start, :return_tw_end, :available_seats,
                :accepts_packages, 
                ST_SetSRID(ST_MakePoint(:origin_lon, :origin_lat), 4326),
                ST_SetSRID(ST_MakePoint(:dest_lon, :dest_lat), 4326),
                NOW()
            ) RETURNING id, created_at;
        """)
        
        result = db.execute(sql_query, {
            "driver_id": trip_data.driver_id,
            "departure_tw_start": trip_data.departure_tw_start,
            "departure_tw_end": trip_data.departure_tw_end,
            "return_tw_start": trip_data.return_tw_start,
            "return_tw_end": trip_data.return_tw_end,
            "available_seats": trip_data.available_seats,
            "accepts_packages": trip_data.accepts_packages,
            "origin_lon": trip_data.origin_longitude,
            "origin_lat": trip_data.origin_latitude,
            "dest_lon": trip_data.destination_longitude,
            "dest_lat": trip_data.destination_latitude
        })
        
        created_trip = result.fetchone()
        db.commit()
        
        # Return the created trip data
        return {
            "id": created_trip.id,
            "driver_id": trip_data.driver_id,
            "departure_tw_start": trip_data.departure_tw_start,
            "departure_tw_end": trip_data.departure_tw_end,
            "return_tw_start": trip_data.return_tw_start,
            "return_tw_end": trip_data.return_tw_end,
            "available_seats": trip_data.available_seats,
            "status": "SCHEDULED",
            "accepts_packages": trip_data.accepts_packages,
            "is_accepting_bookings": True,
            "created_at": created_trip.created_at,
            "origin_coordinates": f"POINT({trip_data.origin_longitude} {trip_data.origin_latitude})",
            "destination_coordinates": f"POINT({trip_data.destination_longitude} {trip_data.destination_latitude})"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating trip: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating trip: {str(e)}")

# ==================== UTILITY ENDPOINT ====================
@router.get("/drivers/available")
async def get_available_drivers(db: Session = Depends(get_db)):
    """Get list of available drivers for creating trips"""
    try:
        sql_query = """
            SELECT d.id, d.name, d.email, v.license_plate, v.seat_capacity
            FROM drivers d
            JOIN vehicles v ON d.vehicle_id = v.id
            WHERE v.is_active = true
            ORDER BY d.name
        """
        
        result = db.execute(text(sql_query))
        drivers = []
        
        for row in result:
            driver_dict = {
                "id": row.id,
                "name": row.name,
                "email": row.email,
                "license_plate": row.license_plate,
                "seat_capacity": row.seat_capacity
            }
            drivers.append(driver_dict)
        
        return drivers
        
    except Exception as e:
        logger.error(f"Error getting available drivers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving drivers: {str(e)}")

# ==================== DEBUGGING ENDPOINT ====================
@router.get("/debug/count")
async def get_trip_counts(db: Session = Depends(get_db)):
    """Debug endpoint to check database state"""
    try:
        # Get trip count
        trip_count = db.execute(text("SELECT COUNT(*) FROM pre_scheduled_trips")).scalar()
        
        # Get driver count
        driver_count = db.execute(text("SELECT COUNT(*) FROM drivers")).scalar()
        
        # Get recent trips
        recent_trips = db.execute(text("""
            SELECT id, driver_id, status, created_at 
            FROM pre_scheduled_trips 
            ORDER BY created_at DESC 
            LIMIT 5
        """)).fetchall()
        
        return {
            "total_trips": trip_count,
            "total_drivers": driver_count,
            "recent_trips": [
                {
                    "id": trip.id,
                    "driver_id": trip.driver_id,
                    "status": trip.status,
                    "created_at": trip.created_at
                }
                for trip in recent_trips
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug error: {str(e)}")

# ==================== TEST DATA CREATION ====================
@router.post("/create-test-data")
async def create_test_prescheduled_trips(db: Session = Depends(get_db)):
    """Create some test pre-scheduled trips for testing"""
    try:
        # Check if we have drivers first
        driver_count = db.execute(text("SELECT COUNT(*) FROM drivers")).scalar()
        if driver_count == 0:
            raise HTTPException(status_code=400, detail="No drivers available. Please create drivers first.")
        
        # Get available driver IDs
        available_drivers = db.execute(text("SELECT id FROM drivers LIMIT 5")).fetchall()
        driver_ids = [driver.id for driver in available_drivers]
        
        test_trips = []
        base_time = datetime.now()
        
        for i, driver_id in enumerate(driver_ids):
            departure_start = base_time + timedelta(hours=24 + i*2)
            departure_end = departure_start + timedelta(hours=2)
            return_start = departure_end + timedelta(hours=8)
            return_end = return_start + timedelta(hours=2)
            
            # Amman area coordinates
            origin_lat = 31.95 + (i * 0.01)
            origin_lon = 35.92 + (i * 0.01)
            dest_lat = 31.96 + (i * 0.01)
            dest_lon = 35.93 + (i * 0.01)
            
            sql_query = text("""
                INSERT INTO pre_scheduled_trips (
                    driver_id, departure_tw_start, departure_tw_end,
                    return_tw_start, return_tw_end, available_seats,
                    accepts_packages, origin_location, destination_location
                ) VALUES (
                    :driver_id, :departure_tw_start, :departure_tw_end,
                    :return_tw_start, :return_tw_end, :available_seats,
                    :accepts_packages,
                    ST_SetSRID(ST_MakePoint(:origin_lon, :origin_lat), 4326),
                    ST_SetSRID(ST_MakePoint(:dest_lon, :dest_lat), 4326)
                ) RETURNING id;
            """)
            
            result = db.execute(sql_query, {
                "driver_id": driver_id,
                "departure_tw_start": departure_start,
                "departure_tw_end": departure_end,
                "return_tw_start": return_start,
                "return_tw_end": return_end,
                "available_seats": 3 + i,
                "accepts_packages": i % 2 == 0,
                "origin_lon": origin_lon,
                "origin_lat": origin_lat,
                "dest_lon": dest_lon,
                "dest_lat": dest_lat
            })
            
            trip_id = result.fetchone().id
            test_trips.append({
                "trip_id": trip_id,
                "driver_id": driver_id,
                "departure_time": departure_start,
                "available_seats": 3 + i
            })
        
        db.commit()
        
        return {
            "message": f"Created {len(test_trips)} test trips successfully",
            "trips": test_trips
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating test data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating test data: {str(e)}")