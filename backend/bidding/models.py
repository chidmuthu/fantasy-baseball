from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from teams.models import Team
from prospects.models import Prospect


class Bid(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE, related_name='bids')
    nominator = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='nominated_bids')
    current_bidder = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='winning_bids')
    starting_bid = models.IntegerField(validators=[MinValueValidator(5)])
    current_bid = models.IntegerField(validators=[MinValueValidator(5)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_bid_time = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['prospect']),
            models.Index(fields=['current_bidder']),
            models.Index(fields=['last_bid_time']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.prospect.name} - {self.current_bid} POM by {self.current_bidder.name}"
    
    @property
    def time_remaining(self):
        """Calculate time remaining until bid completion"""
        if self.status != 'active' or not self.expires_at:
            return None
        
        time_remaining = (self.expires_at - timezone.now()).total_seconds() / 60
        
        if time_remaining <= 0:
            return 0
        return time_remaining
    
    @property
    def is_expired(self):
        """Check if bid has expired"""
        return self.expires_at and timezone.now() >= self.expires_at
    
    def update_expiration_time(self):
        """Update the expiration time based on current settings"""
        from django.conf import settings
        expiration_minutes = getattr(settings, 'BID_EXPIRATION_MINUTES', 1440)
        self.expires_at = timezone.now() + timezone.timedelta(minutes=expiration_minutes)
        self.save(update_fields=['expires_at'])
    
    def place_bid(self, team, amount):
        """Place a new bid on this auction"""
        if self.status != 'active':
            raise ValueError("Cannot bid on inactive auction")
        
        if amount <= self.current_bid:
            raise ValueError("Bid must be higher than current bid")
        
        if not team.can_afford_bid(amount):
            raise ValueError("Team cannot afford this bid")
        
        # Record the bid in history
        BidHistory.objects.create(
            bid=self,
            team=team,
            amount=amount
        )
        
        # Update the current bid
        self.current_bid = amount
        self.current_bidder = team
        self.last_bid_time = timezone.now()
        
        # Save the changes to the database
        self.save()
        
        # Update expiration time (extends the bid when someone bids)
        self.update_expiration_time()
        
        # Trigger real-time notification
        try:
            from .tasks import notify_new_bid
            notify_new_bid.delay(self.id)
        except Exception as e:
            print(f"Warning: Could not send bid notification: {e}")
        
        return True
    
    def complete_bid(self):
        """Complete the bid and transfer prospect to winning team"""
        if self.status != 'active':
            return False
        
        # Deduct POM from winning team
        if not self.current_bidder.deduct_pom(self.current_bid):
            return False
        
        # Transfer prospect to winning team
        self.prospect.transfer_to_team(self.current_bidder)
        
        # Mark bid as completed
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
        return True
    
    def cancel_bid(self):
        """Cancel the bid (admin only)"""
        self.status = 'cancelled'
        self.completed_at = timezone.now()
        self.save()


class BidHistory(models.Model):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name='history')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    amount = models.IntegerField()
    bid_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-bid_time']
        indexes = [
            models.Index(fields=['bid']),
            models.Index(fields=['team']),
            models.Index(fields=['bid_time']),
        ]
    
    def __str__(self):
        return f"{self.team.name} bid {self.amount} POM at {self.bid_time}" 