from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from teams.models import Team
from prospects.models import Prospect
from bidding.models import Bid
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Create test data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing test data...')
            User.objects.filter(username__startswith='test_').delete()
            Prospect.objects.filter(created_by__name__startswith='Test Team').delete()
            Bid.objects.filter(nominator__name__startswith='Test Team').delete()

        self.stdout.write('Creating test data...')

        # Create test teams
        test_teams = []
        team_names = [
            'Test Team Alpha',
            'Test Team Beta', 
            'Test Team Gamma',
            'Test Team Delta',
            'Test Team Echo'
        ]

        for i, name in enumerate(team_names):
            username = f'test_user_{i+1}'
            email = f'{username}@test.com'
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password='testpass123',
                first_name=f'Test{i+1}',
                last_name='User'
            )
            
            # Update team name
            team = user.team
            team.name = name
            team.pom_balance = 100 + (i * 25)  # Different POM amounts
            team.save()
            
            test_teams.append(team)
            self.stdout.write(f'Created {name} (POM: {team.pom_balance})')

        # Create test prospects
        prospect_data = [
            {'name': 'Jackson Holliday', 'position': 'SS', 'organization': 'Baltimore Orioles', 'date_of_birth': '2003-01-01', 'level': 'A', 'eta': 2025},
            {'name': 'Junior Caminero', 'position': '3B', 'organization': 'Tampa Bay Rays', 'date_of_birth': '2003-03-02', 'level': 'A', 'eta': 2025},
            {'name': 'Wyatt Flores', 'position': 'P', 'organization': 'Milwaukee Brewers', 'date_of_birth': '2004-05-03', 'level': 'A+', 'eta': 2027},
            {'name': 'Ethan Salas', 'position': 'C', 'organization': 'San Diego Padres', 'date_of_birth': '2006-07-04', 'level': 'AAA', 'eta': 2025},
            {'name': 'Jackson Chourio', 'position': 'OF', 'organization': 'Milwaukee Brewers', 'date_of_birth': '2004-09-05', 'level': 'A', 'eta': 2025},
            {'name': 'Paul Skenes', 'position': 'P', 'organization': 'Pittsburgh Pirates', 'date_of_birth': '2002-11-06', 'level': 'MLB', 'eta': 2024},
            {'name': 'Dylan Crews', 'position': 'OF', 'organization': 'Washington Nationals', 'date_of_birth': '2002-12-07', 'level': 'AA', 'eta': 2026},
            {'name': 'Roki Sasaki', 'position': 'P', 'organization': 'Los Angeles Dodgers', 'date_of_birth': '2001-02-08', 'level': 'ROK', 'eta': 2028},
        ]

        prospects = []
        for data in prospect_data:
            prospect = Prospect.objects.create(
                **data,
                created_by=test_teams[0]
            )
            prospects.append(prospect)
            self.stdout.write(f'Created prospect: {prospect.name}')

        # Create bids with different starting times
        bid_start_times = [
            timezone.now() - timedelta(minutes=2),  # Recently started
            timezone.now() - timedelta(minutes=10),  # Started 10 minutes ago
            timezone.now() - timedelta(minutes=30),  # Started 30 minutes ago
        ]

        for i, prospect in enumerate(prospects[:3]):  # Create bids for first 3 prospects
            nominator = test_teams[i % len(test_teams)]
            starting_bid = 5 + (i * 2)  # Different starting bids
            
            # Create bid with custom start time
            bid = Bid.objects.create(
                prospect=prospect,
                nominator=nominator,
                current_bidder=nominator,
                starting_bid=starting_bid,
                current_bid=starting_bid,
                status='active',
                expires_at=timezone.now() + timedelta(minutes=5)
            )
            
            # Manually set the timestamps for testing
            bid.created_at = bid_start_times[i % len(bid_start_times)]
            bid.last_bid_time = bid.created_at
            bid.save()
            
            self.stdout.write(f'Created bid for {prospect.name} - {starting_bid} POM by {nominator.name}')

        # Create some completed bids
        completed_prospects = prospects[3:6]
        for i, prospect in enumerate(completed_prospects):
            nominator = test_teams[i % len(test_teams)]
            winner = test_teams[(i + 1) % len(test_teams)]
            final_bid = 8 + (i * 3)
            
            # Create completed bid
            bid = Bid.objects.create(
                prospect=prospect,
                nominator=nominator,
                current_bidder=winner,
                starting_bid=5,
                current_bid=final_bid,
                status='completed',
                completed_at=timezone.now() - timedelta(hours=1)
            )
            
            # Transfer prospect to winner
            prospect.team = winner
            prospect.acquired_at = bid.completed_at
            prospect.save()
            
            # Deduct POM from winner
            winner.pom_balance -= final_bid
            winner.save()
            
            self.stdout.write(f'Created completed bid: {prospect.name} won by {winner.name} for {final_bid} POM')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTest data created successfully!\n'
                f'- {len(test_teams)} teams\n'
                f'- {len(prospects)} prospects\n'
                f'- 3 active bids\n'
                f'- 3 completed bids\n\n'
                f'Test accounts:\n'
                f'Username: test_user_1, Password: testpass123\n'
                f'Username: test_user_2, Password: testpass123\n'
                f'Username: test_user_3, Password: testpass123\n'
                f'Username: test_user_4, Password: testpass123\n'
                f'Username: test_user_5, Password: testpass123\n\n'
                f'Admin account: Use your superuser credentials\n\n'
            )
        ) 