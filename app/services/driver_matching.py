# app/services/driver_matching.py - FIXED VERSION
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.ride_request import DriverMatchRequest, DriverMatchResponse
import json
import logging

logger = logging.getLogger(__name__)

class DriverMatchingService:
    
    @staticmethod
    def find_matching_drivers(
        db: Session,
        request: DriverMatchRequest
    ) -> List[DriverMatchResponse]:
        """
        Find matching drivers using the PostgreSQL function
        """
        try:
            # Convert feature_preferences to JSON string
            if request.feature_preferences:
                feature_preferences_dict = {
                    "required": request.feature_preferences.required or [],
                    "optional": request.feature_preferences.optional or []
                }
                feature_preferences_json = json.dumps(feature_preferences_dict)
            else:
                feature_preferences_json = json.dumps({"required": [], "optional": []})
            
            logger.info(f"Feature preferences JSON: {feature_preferences_json}")
            
            # Use raw connection to avoid SQLAlchemy parameter issues
            connection = db.connection()
            
            # Raw SQL query exactly like your working pgAdmin query
            sql_query = """
                SELECT * FROM find_matching_drivers_direct(
                    p_pickup_location := ST_SetSRID(ST_MakePoint(%(pickup_lon)s, %(pickup_lat)s), 4326),
                    p_dropoff_location := ST_SetSRID(ST_MakePoint(%(dropoff_lon)s, %(dropoff_lat)s), 4326),
                    p_pickup_tw_start := %(pickup_tw_start)s::TIMESTAMP WITHOUT TIME ZONE,
                    p_pickup_tw_end := %(pickup_tw_end)s::TIMESTAMP WITHOUT TIME ZONE,
                    p_seats_required := %(seats_required)s,
                    p_wheelchair_needed := %(wheelchair_needed)s,
                    p_feature_preferences := %(feature_preferences)s::jsonb,
                    p_max_results := %(max_results)s,
                    p_max_distance_meters := %(max_distance_meters)s,
                    p_max_waiting_minutes := %(max_waiting_minutes)s
                );
            """
            
            # Prepare parameters
            params = {
                "pickup_lon": float(request.pickup_longitude),
                "pickup_lat": float(request.pickup_latitude),
                "dropoff_lon": float(request.dropoff_longitude),
                "dropoff_lat": float(request.dropoff_latitude),
                "pickup_tw_start": request.pickup_tw_start,
                "pickup_tw_end": request.pickup_tw_end,
                "seats_required": int(request.seats_required),
                "wheelchair_needed": bool(request.wheelchair_needed),
                "feature_preferences": feature_preferences_json,
                "max_results": int(request.max_results),
                "max_distance_meters": int(request.max_distance_meters),
                "max_waiting_minutes": int(request.max_waiting_minutes)
            }
            
            logger.info(f"Executing query with params: {params}")
            
            # Execute using raw psycopg2 cursor
            with connection.connection.cursor() as cursor:
                cursor.execute(sql_query, params)
                columns = [desc[0] for desc in cursor.description]
                results = cursor.fetchall()
                
                logger.info(f"Query returned {len(results)} rows")
                
                # Convert results to response objects
                matches = []
                for row_data in results:
                    row_dict = dict(zip(columns, row_data))
                    
                    # Handle available_features array
                    available_features = []
                    if row_dict.get('available_features'):
                        available_features = list(row_dict['available_features'])
                    
                    match = DriverMatchResponse(
                        driver_id=int(row_dict['driver_id']),
                        driver_name=str(row_dict['driver_name']),
                        vehicle_id=int(row_dict['vehicle_id']),
                        distance_to_pickup=float(row_dict['distance_to_pickup']),
                        estimated_arrival_time=row_dict['estimated_arrival_time'],
                        travel_time_minutes=float(row_dict['travel_time_minutes']),
                        seat_capacity=int(row_dict['seat_capacity']),
                        has_wheelchair_access=bool(row_dict['has_wheelchair_access']),
                        available_features=available_features,
                        match_score=float(row_dict['match_score']) if row_dict['match_score'] is not None else 0.0,
                        proximity_score=float(row_dict['proximity_score']) if row_dict['proximity_score'] is not None else 0.0,
                        temporal_score=float(row_dict['temporal_score']) if row_dict['temporal_score'] is not None else 0.0,
                        vehicle_score=float(row_dict['vehicle_score']) if row_dict['vehicle_score'] is not None else 0.0,
                        feature_score=float(row_dict['feature_score']) if row_dict['feature_score'] is not None else 0.0,
                        estimated_fare=float(row_dict['estimated_fare']) if row_dict['estimated_fare'] is not None else 0.0
                    )
                    matches.append(match)
                
                logger.info(f"Successfully processed {len(matches)} matching drivers")
                return matches
            
        except Exception as e:
            logger.error(f"Error in find_matching_drivers: {str(e)}")
            logger.error(f"Request data: {request}")
            raise Exception(f"Driver matching failed: {str(e)}")
