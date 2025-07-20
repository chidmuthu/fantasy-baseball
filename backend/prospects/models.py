from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date
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
    
    LEVEL_CHOICES = [
        ('ROK', 'Rookie'),
        ('A', 'A'),
        ('A+', 'A+'),
        ('AA', 'AA'),
        ('AAA', 'AAA'),
        ('MLB', 'MLB'),
    ]
    
    # Basic info
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=10, choices=POSITION_CHOICES)
    organization = models.CharField(max_length=100)  # MLB team
    date_of_birth = models.DateField()
    level = models.CharField(max_length=3, choices=LEVEL_CHOICES, default='A')
    eta = models.IntegerField(help_text="Expected year of MLB arrival")
    
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
            models.Index(fields=['level']),
            models.Index(fields=['eta'])
        ]
    
    def __str__(self):
        return f"{self.name} ({self.position}) - {self.organization}"
    
    @property
    def age(self):
        """Calculate decimal age dynamically based on date of birth"""
        today = date.today()
        
        # Calculate base age
        age = today.year - self.date_of_birth.year
        
        # Calculate months since last birthday
        months_since_birthday = (today.month - self.date_of_birth.month) % 12
        
        # Adjust for if birthday hasn't occurred this year
        if today.month < self.date_of_birth.month or (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1
            months_since_birthday = (12 + today.month - self.date_of_birth.month) % 12
        
        # Convert months to decimal (approximate)
        decimal_age = age + (months_since_birthday / 12.0)
        
        # Round to 1 decimal place for simplicity
        return round(decimal_age, 2)
    
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