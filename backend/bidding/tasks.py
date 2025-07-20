from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from .models import Bid


@shared_task
def check_expired_bids():
    """Check for expired bids and complete them automatically"""
    from django.utils import timezone
    
    # Find bids that have expired (expires_at is in the past)
    expired_bids = Bid.objects.filter(
        status='active',
        expires_at__lt=timezone.now()
    )
    
    print(f"🔍 Checking for expired bids...")
    print(f"   Current time: {timezone.now()}")
    print(f"   Found {expired_bids.count()} expired bids")
    
    completed_count = 0
    for bid in expired_bids:
        try:
            if bid.complete_bid():
                completed_count += 1
                
                # Send real-time notification to all connected clients
                notify_bid_completed.delay(bid.id)
                
                print(f"✅ Automatically completed bid for {bid.prospect.name} - {bid.current_bidder.name} wins for {bid.current_bid} POM")
            else:
                print(f"❌ Failed to complete bid for {bid.prospect.name}")
        except Exception as e:
            print(f"❌ Error completing bid for {bid.prospect.name}: {str(e)}")
    
    if completed_count > 0:
        print(f"🎉 Successfully completed {completed_count} expired bids")
    
    return completed_count


@shared_task
def notify_bid_completed(bid_id):
    """Send WebSocket notification when a bid is completed"""
    try:
        bid = Bid.objects.get(id=bid_id)
        channel_layer = get_channel_layer()
        
        # Prepare notification data
        notification_data = {
            'type': 'bid_completed',
            'bid_id': bid.id,
            'data': {
                'prospect_name': bid.prospect.name,
                'prospect_position': bid.prospect.position,
                'winning_team': bid.current_bidder.name,
                'winning_amount': bid.current_bid,
                'completed_at': bid.completed_at.isoformat() if bid.completed_at else None,
            }
        }
        
        # Send to general bidding channel
        async_to_sync(channel_layer.group_send)(
            "bidding_updates",
            {
                'type': 'bid_completed',
                'bid_id': bid.id,
                'data': notification_data['data']
            }
        )
        
        # Send to winning team's specific channel
        async_to_sync(channel_layer.group_send)(
            f"team_{bid.current_bidder.id}",
            {
                'type': 'prospect_acquired',
                'data': {
                    'prospect_name': bid.prospect.name,
                    'prospect_position': bid.prospect.position,
                    'amount_paid': bid.current_bid,
                    'new_balance': bid.current_bidder.pom_balance,
                    'acquired_at': bid.completed_at.isoformat() if bid.completed_at else None,
                }
            }
        )
        
        print(f"📢 Sent WebSocket notifications for completed bid: {bid.prospect.name}")
        
    except Bid.DoesNotExist:
        print(f"❌ Bid {bid_id} not found for notification")
    except Exception as e:
        print(f"❌ Error sending bid completion notification: {str(e)}")


@shared_task
def notify_new_bid(bid_id):
    """Send WebSocket notification when a new bid is placed"""
    try:
        bid = Bid.objects.get(id=bid_id)
        channel_layer = get_channel_layer()
        
        notification_data = {
            'prospect_name': bid.prospect.name,
            'prospect_position': bid.prospect.position,
            'current_bid': bid.current_bid,
            'current_bidder': bid.current_bidder.name,
            'time_remaining': bid.time_remaining,
            'bid_id': bid.id,
        }
        
        # Send to general bidding channel
        async_to_sync(channel_layer.group_send)(
            "bidding_updates",
            {
                'type': 'bid_update',
                'bid_id': bid.id,
                'data': notification_data
            }
        )
        
        # Send to specific bid channel
        async_to_sync(channel_layer.group_send)(
            f"bid_{bid.id}",
            {
                'type': 'bid_update',
                'bid_id': bid.id,
                'data': notification_data
            }
        )
        
        print(f"📢 Sent WebSocket notifications for new bid: {bid.prospect.name}")
        
    except Bid.DoesNotExist:
        print(f"❌ Bid {bid_id} not found for notification")
    except Exception as e:
        print(f"❌ Error sending new bid notification: {str(e)}")


# @shared_task
# def cleanup_old_bids():
#     """Clean up old completed/cancelled bids (optional maintenance task)"""
#     from datetime import timedelta
    
#     # Remove bids older than 30 days
#     cutoff_date = timezone.now() - timedelta(days=30)
#     old_bids = Bid.objects.filter(
#         status__in=['completed', 'cancelled'],
#         completed_at__lt=cutoff_date
#     )
    
#     count = old_bids.count()
#     old_bids.delete()
    
#     if count > 0:
#         print(f"🧹 Cleaned up {count} old bids")
    
#     return count 