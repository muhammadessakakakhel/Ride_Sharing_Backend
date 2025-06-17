from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.pre_scheduled_trip import PreScheduledTripMatchRequest, PreScheduledTripMatchResponse
import json
import logging

logger = logging.getLogger(__name__)

class PreScheduledTripMatchingService:
    
    @staticmethod
    def find_matching_prescheduled_trips(
        db: Session,
        request: PreScheduledTripMatchRequest
    ) -> List[PreScheduledTripMatchResponse]:
        """
        Find matching pre-scheduled trips using the PostgreSQL function
        """
        try:
            # Convert feature_preferences to JSON string (SAME AS DIRECT MATCHING)
            if request.feature_preferences:
                # Handle both dict and FeaturePreferences object
                if hasattr(request.feature_preferences, 'required'):
                    # It's a FeaturePreferences object
                    feature_preferences_dict = {
                        "required": request.feature_preferences.required or [],
                        "optional": request.feature_preferences.optional or []
                    }
                else:
                    # It's already a dict
                    feature_preferences_dict = request.feature_preferences
                
                feature_preferences_json = json.dumps(feature_preferences_dict)
            else:
                feature_preferences_json = json.dumps({"required": [], "optional": []})
            
            logger.info(f"Feature preferences JSON: {feature_preferences_json}")
            
            # Use raw connection to avoid SQLAlchemy parameter issues (SAME AS DIRECT MATCHING)
            connection = db.connection()
            
            # Raw SQL query exactly like your working pgAdmin query
            sql_query = """
                SELECT * FROM find_matching_prescheduled_trips_direct(
                    p_pickup_location := ST_SetSRID(ST_MakePoint(%(pickup_lon)s, %(pickup_lat)s), 4326),
                    p_dropoff_location := ST_SetSRID(ST_MakePoint(%(dropoff_lon)s, %(dropoff_lat)s), 4326),
                    p_pickup_tw_start := %(pickup_tw_start)s::TIMESTAMP WITHOUT TIME ZONE,
                    p_pickup_tw_end := %(pickup_tw_end)s::TIMESTAMP WITHOUT TIME ZONE,
                    p_seats_required := %(seats_required)s,
                    p_wheelchair_needed := %(wheelchair_needed)s,
                    p_feature_preferences := %(feature_preferences)s::jsonb,
                    p_max_results := %(max_results)s,
                    p_max_pickup_distance_meters := %(max_pickup_distance_meters)s,
                    p_max_dropoff_distance_meters := %(max_dropoff_distance_meters)s,
                    p_max_time_window_minutes := %(max_time_window_minutes)s
                );
            """
            
            # Prepare parameters (SAME PATTERN AS DIRECT MATCHING)
            params = {
                "pickup_lon": float(request.pickup_longitude),
                "pickup_lat": float(request.pickup_latitude),
                "dropoff_lon": float(request.dropoff_longitude),
                "dropoff_lat": float(request.dropoff_latitude),
                "pickup_tw_start": request.pickup_tw_start,
                "pickup_tw_end": request.pickup_tw_end,
                "seats_required": int(request.seats_required),
                "wheelchair_needed": bool(request.wheelchair_needed),
                "feature_preferences": feature_preferences_json,  # JSON STRING, NOT DICT
                "max_results": int(request.max_results),
                "max_pickup_distance_meters": int(request.max_pickup_distance_meters),
                "max_dropoff_distance_meters": int(request.max_dropoff_distance_meters),
                "max_time_window_minutes": int(request.max_time_window_minutes)
            }
            
            logger.info(f"Executing query with params: {params}")
            
            # Execute using raw psycopg2 cursor (SAME AS DIRECT MATCHING)
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
                    
                    match = PreScheduledTripMatchResponse(
                        trip_id=int(row_dict['trip_id']),
                        driver_id=int(row_dict['driver_id']),
                        driver_name=str(row_dict['driver_name']),
                        driver_gender=str(row_dict['driver_gender']) if row_dict['driver_gender'] else None,
                        vehicle_license_plate=str(row_dict['vehicle_license_plate']),
                        available_seats=int(row_dict['available_seats']),
                        departure_tw_start=row_dict['departure_tw_start'],
                        departure_tw_end=row_dict['departure_tw_end'],
                        return_tw_start=row_dict['return_tw_start'],
                        return_tw_end=row_dict['return_tw_end'],
                        pickup_distance_meters=float(row_dict['pickup_distance_meters']),
                        dropoff_distance_meters=float(row_dict['dropoff_distance_meters']),
                        time_difference_minutes=int(row_dict['time_difference_minutes']),
                        origin_coordinates=str(row_dict['origin_coordinates']),
                        destination_coordinates=str(row_dict['destination_coordinates']),
                        has_wheelchair_access=bool(row_dict['has_wheelchair_access']),
                        available_features=available_features,
                        accepts_packages=bool(row_dict['accepts_packages']),
                        match_score=float(row_dict['match_score']) if row_dict['match_score'] is not None else 0.0,
                        distance_score=float(row_dict['distance_score']) if row_dict['distance_score'] is not None else 0.0,
                        time_score=float(row_dict['time_score']) if row_dict['time_score'] is not None else 0.0,
                        feature_score=float(row_dict['feature_score']) if row_dict['feature_score'] is not None else 0.0,
                        capacity_utilization=float(row_dict['capacity_utilization']) if row_dict['capacity_utilization'] is not None else 0.0
                    )
                    matches.append(match)
                
                logger.info(f"Successfully processed {len(matches)} matching trips")
                return matches
            
        except Exception as e:
            logger.error(f"Error in find_matching_prescheduled_trips: {str(e)}")
            logger.error(f"Request data: {request}")
            raise Exception(f"Pre-scheduled trip matching failed: {str(e)}")