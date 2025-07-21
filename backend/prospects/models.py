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
    
    # Eligibility tracking
    at_bats = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    innings_pitched = models.DecimalField(max_digits=6, decimal_places=1, default=0.0, validators=[MinValueValidator(0)])
    tags_applied = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    last_tagged_at = models.DateTimeField(null=True, blank=True)
    last_tagged_by = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='tagged_prospects')
    
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
            models.Index(fields=['eta']),
            models.Index(fields=['tags_applied']),
            models.Index(fields=['last_tagged_by']),
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
    
    @property
    def eligibility_threshold_ab(self):
        """Get the at-bats threshold for eligibility (140 base, +140 per tag)"""
        return 140 + (self.tags_applied * 140)
    
    @property
    def eligibility_threshold_ip(self):
        """Get the innings pitched threshold for eligibility (50 base, +50 per tag)"""
        return 50 + (self.tags_applied * 50)
    
    @property
    def is_eligible(self):
        """Check if prospect is still eligible (hasn't exceeded thresholds)"""
        return (self.at_bats < self.eligibility_threshold_ab and 
                float(self.innings_pitched) < self.eligibility_threshold_ip)
    
    @property
    def eligibility_status(self):
        """Get a human-readable eligibility status"""
        if self.is_eligible:
            ab_remaining = self.eligibility_threshold_ab - self.at_bats
            ip_remaining = self.eligibility_threshold_ip - float(self.innings_pitched)
            
            if self.position == 'P':
                return f"Eligible ({ip_remaining:.1f} IP remaining)"
            else:
                return f"Eligible ({ab_remaining} AB remaining)"
        else:
            return "Ineligible"
    
    @property
    def next_tag_cost(self):
        """Calculate the cost for the next tag (5, 10, 20, 40, etc.)"""
        return 5 * (2 ** self.tags_applied)
    
    def tag_prospect(self, team):
        """Tag a prospect to extend eligibility (cost doubles each time)"""
        
        tag_cost = self.next_tag_cost
        if team.pom_balance < tag_cost:
            raise ValueError(f"Team does not have enough POM to tag prospect (cost: {tag_cost} POM)")
        
        # Deduct POM from team
        team.pom_balance -= tag_cost
        team.save()
        
        # Tag the prospect
        self.tags_applied += 1
        self.last_tagged_at = timezone.now()
        self.last_tagged_by = team
        self.save()
    
    def transfer_to_team(self, new_team):
        """Transfer prospect to a new team"""
        self.team = new_team
        self.acquired_at = timezone.now()
        self.save() 