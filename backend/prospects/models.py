from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from teams.models import Team


class Prospect(models.Model):
    POSITION_CHOICES = [
        ('P', 'Pitcher'),
        ('C', 'Catcher'),
        ('1B', 'First Base'),
        ('2B', 'Second Base'),
        ('3B', 'Third Base'),
        ('SS', 'Shortstop'),
        ('OF', 'Outfield'),
        ('UTIL', 'Utility'),
    ]
    
    # Basic info
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=10, choices=POSITION_CHOICES)
    organization = models.CharField(max_length=100)  # MLB team
    age = models.IntegerField(validators=[MinValueValidator(16), MaxValueValidator(30)])
    notes = models.TextField(blank=True)
    
    # Farm system
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='prospects')
    acquired_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='created_prospects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['team']),
            models.Index(fields=['organization']),
            models.Index(fields=['position']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.position}) - {self.organization}"
    
    @property
    def is_available(self):
        """Check if prospect is available for bidding (not on any team)"""
        return self.team is None
    
    @property
    def current_bid(self):
        """Get the current active bid for this prospect"""
        return self.bids.filter(status='active').first()
    
    def transfer_to_team(self, new_team):
        """Transfer prospect to a new team"""
        self.team = new_team
        self.acquired_at = timezone.now()
        self.save() 