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
    
    for prospect in prospects:
        try:
            # Get current MLB stats
            is_pitcher = prospect.position == 'P'
            count = baseball_service.get_mlb_appearances(prospect.name, pitching=is_pitcher)
            
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


@shared_task
def update_single_prospect_stats(prospect_id):
    """
    Update stats for a single prospect (useful for manual updates)
    """
    try:
        prospect = Prospect.objects.get(id=prospect_id)
        baseball_service = get_baseball_data_service()
        is_pitcher = prospect.position == 'P'
        
        count = baseball_service.get_mlb_appearances(prospect.name, pitching=is_pitcher)
        
        # Update the prospect
        if is_pitcher:
            prospect.innings_pitched = count
        else:
            prospect.at_bats = count
        prospect.save()
        
        logger.info(f"Updated {prospect.name}: {prospect.at_bats} AB, {prospect.innings_pitched} IP")
        
        return {
            'prospect_id': prospect_id,
            'prospect_name': prospect.name,
            'at_bats': prospect.at_bats,
            'innings_pitched': prospect.innings_pitched,
            'is_eligible': prospect.is_eligible
        }
        
    except Prospect.DoesNotExist:
        logger.error(f"Prospect with ID {prospect_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error updating prospect {prospect_id}: {e}")
        return None
