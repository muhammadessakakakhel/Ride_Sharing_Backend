from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.schemas.ride_request import DriverMatchRequest
from app.schemas.pre_scheduled_trip import PreScheduledTripMatchRequest
from app.services.driver_matching import DriverMatchingService
from app.services.prescheduled_trip_matching import PreScheduledTripMatchingService

class CombinedRideService:
    """
    Service that combines both direct driver matching and pre-scheduled trip matching
    to provide comprehensive ride options
    """
    
    @staticmethod
    def find_all_ride_options(
        db: Session,
        pickup_latitude: float,
        pickup_longitude: float,
        dropoff_latitude: float,
        dropoff_longitude: float,
        pickup_tw_start: datetime,
        pickup_tw_end: datetime,
        seats_required: int = 1,
        wheelchair_needed: bool = False,
        feature_preferences: Optional[Dict[str, Any]] = None,
        max_results_per_type: int = 5
    ) -> Dict[str, Any]:
        """
        Find both direct drivers and pre-scheduled trips for a ride request
        """
        
        # Create requests for both algorithms
        direct_request = DriverMatchRequest(
            pickup_latitude=pickup_latitude,
            pickup_longitude=pickup_longitude,
            dropoff_latitude=dropoff_latitude,
            dropoff_longitude=dropoff_longitude,
            pickup_tw_start=pickup_tw_start,
            pickup_tw_end=pickup_tw_end,
            seats_required=seats_required,
            wheelchair_needed=wheelchair_needed,
            feature_preferences=feature_preferences,
            max_results=max_results_per_type
        )
        
        prescheduled_request = PreScheduledTripMatchRequest(
            pickup_latitude=pickup_latitude,
            pickup_longitude=pickup_longitude,
            dropoff_latitude=dropoff_latitude,
            dropoff_longitude=dropoff_longitude,
            pickup_tw_start=pickup_tw_start,
            pickup_tw_end=pickup_tw_end,
            seats_required=seats_required,
            wheelchair_needed=wheelchair_needed,
            feature_preferences=feature_preferences,
            max_results=max_results_per_type,
            max_pickup_distance_meters=15000,
            max_dropoff_distance_meters=15000,
            max_time_window_minutes=1440  # 24 hours
        )
        
        try:
            # Get direct driver matches
            direct_matches = DriverMatchingService.find_matching_drivers(db, direct_request)
            
            # Get pre-scheduled trip matches  
            prescheduled_matches = PreScheduledTripMatchingService.find_matching_prescheduled_trips(
                db, prescheduled_request
            )
            
            return {
                "request_summary": {
                    "pickup_location": {"latitude": pickup_latitude, "longitude": pickup_longitude},
                    "dropoff_location": {"latitude": dropoff_latitude, "longitude": dropoff_longitude},
                    "pickup_time_window": {"start": pickup_tw_start, "end": pickup_tw_end},
                    "seats_required": seats_required,
                    "wheelchair_needed": wheelchair_needed,
                    "feature_preferences": feature_preferences
                },
                "direct_drivers": {
                    "count": len(direct_matches),
                    "matches": direct_matches,
                    "description": "Available drivers for immediate pickup"
                },
                "prescheduled_trips": {
                    "count": len(prescheduled_matches),
                    "matches": prescheduled_matches,
                    "description": "Existing scheduled trips you can join"
                },
                "recommendations": CombinedRideService._generate_recommendations(
                    direct_matches, prescheduled_matches
                )
            }
            
        except Exception as e:
            raise Exception(f"Error finding ride options: {str(e)}")
    
    @staticmethod
    def _generate_recommendations(direct_matches, prescheduled_matches) -> Dict[str, Any]:
        """Generate recommendations based on available options"""
        recommendations = []
        
        if direct_matches and prescheduled_matches:
            best_direct = max(direct_matches, key=lambda x: x.match_score)
            best_prescheduled = max(prescheduled_matches, key=lambda x: x.match_score)
            
            if best_direct.match_score > best_prescheduled.match_score:
                recommendations.append({
                    "type": "immediate",
                    "reason": "Higher match score available for immediate pickup",
                    "option": "direct_driver"
                })
            else:
                recommendations.append({
                    "type": "scheduled", 
                    "reason": "Better match available with scheduled trip",
                    "option": "prescheduled_trip"
                })
                
        elif direct_matches:
            recommendations.append({
                "type": "immediate",
                "reason": "Only immediate drivers available",
                "option": "direct_driver"
            })
            
        elif prescheduled_matches:
            recommendations.append({
                "type": "scheduled",
                "reason": "Only scheduled trips available", 
                "option": "prescheduled_trip"
            })
        else:
            recommendations.append({
                "type": "none",
                "reason": "No matching options found",
                "suggestion": "Try adjusting time window or location"
            })
            
        return {
            "summary": recommendations[0] if recommendations else None,
            "total_options": len(direct_matches) + len(prescheduled_matches)
        }