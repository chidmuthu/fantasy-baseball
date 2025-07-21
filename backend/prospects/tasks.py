from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
from .models import Prospect
from .services import get_baseball_data_service

logger = logging.getLogger(__name__)


@shared_task
def update_prospect_stats():
    """
    Background task to update prospect MLB stats from external sources.
    Runs nightly to keep prospect eligibility data current.
    """
    logger.info("Starting prospect stats update task")
    
    # Get all prospects that might have MLB appearances
    prospects = Prospect.objects.all()
    error_count = 0
    
    baseball_service = get_baseball_data_service()
    players = baseball_service.load_chadwick_data()
    
    for prospect in prospects:
        try:
            # Get current MLB stats
            logger.info(f"Updating stats for {prospect.name}")
            is_pitcher = prospect.position == 'P'
            count = baseball_service.get_mlb_appearances(prospect.name, players, pitching=is_pitcher)
            if count is None:
                logger.warning(f"No stats found for {prospect.name}, minor league only player?")
                continue
            logger.info(f"Found {count} AB or IP for {prospect.name}")
            # Check if stats have changed\
            if is_pitcher:
                prospect.innings_pitched = count
                logger.info(f"Updated {prospect.name}: {count} IP")
            else:
                prospect.at_bats = count
                logger.info(f"Updated {prospect.name}: {count} AB")
                
            prospect.save()    # Log if prospect became ineligible
            if not prospect.is_eligible:
                logger.warning(f"Prospect {prospect.name} is now ineligible due to MLB appearances")
            
        except Exception as e:
            error_count += 1
            logger.error(f"Error updating stats for {prospect.name}: {e}")
    
    return {
        'error_count': error_count,
        'total_prospects': prospects.count()
    }
