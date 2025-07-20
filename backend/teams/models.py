from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='team')
    pom_balance = models.IntegerField(default=100, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def prospect_count(self):
        return self.prospects.count()
    
    def can_afford_bid(self, amount, exclude_bid=None):
        """Check if team can afford a bid amount, considering all active bids"""
        # Get total committed POM from active bids where this team is the current bidder
        from bidding.models import Bid
        committed_pom = Bid.objects.filter(
            current_bidder=self,
            status='active'
        ).exclude(id=exclude_bid.id if exclude_bid else None).aggregate(
            total=models.Sum('current_bid')
        )['total'] or 0
        
        # Available POM = current balance - committed POM
        available_pom = self.pom_balance - committed_pom
        
        logger.info(f"Team {self.name} affordability check:")
        logger.info(f"  - Current balance: {self.pom_balance} POM")
        logger.info(f"  - Committed POM: {committed_pom} POM")
        logger.info(f"  - Available POM: {available_pom} POM")
        logger.info(f"  - Requested amount: {amount} POM")
        logger.info(f"  - Can afford: {available_pom >= amount}")
        
        return available_pom >= amount
    
    def get_available_pom(self, exclude_bid=None):
        """Get the available POM balance (current balance minus committed bids)"""
        from bidding.models import Bid
        committed_pom = Bid.objects.filter(
            current_bidder=self,
            status='active'
        ).exclude(id=exclude_bid.id if exclude_bid else None).aggregate(
            total=models.Sum('current_bid')
        )['total'] or 0
        
        return self.pom_balance - committed_pom
    
    def deduct_pom(self, amount):
        """Deduct POM from team balance"""
        if self.can_afford_bid(amount):
            self.pom_balance -= amount
            self.save()
            return True
        return False
    
    def add_pom(self, amount):
        """Add POM to team balance"""
        self.pom_balance += amount
        self.save()


@receiver(post_save, sender=User)
def create_team_for_user(sender, instance, created, **kwargs):
    """Automatically create a team when a user is created"""
    if created:
        Team.objects.create(
            name=f"{instance.username}'s Team",
            owner=instance
        )


@receiver(post_save, sender=User)
def save_team_for_user(sender, instance, **kwargs):
    """Save team when user is saved"""
    if hasattr(instance, 'team'):
        instance.team.save() 