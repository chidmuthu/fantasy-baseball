from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    
    def can_afford_bid(self, amount):
        """Check if team can afford a bid amount"""
        return self.pom_balance >= amount
    
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