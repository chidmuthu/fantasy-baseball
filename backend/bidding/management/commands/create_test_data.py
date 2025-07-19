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
        parser.add_argument(
            '--fast-bids',
            action='store_true',
            help='Create bids with 5-minute expiration for testing',
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
            {'name': 'Jackson Holliday', 'position': 'SS', 'organization': 'Baltimore Orioles', 'age': 20},
            {'name': 'Junior Caminero', 'position': '3B', 'organization': 'Tampa Bay Rays', 'age': 20},
            {'name': 'Wyatt Flores', 'position': 'P', 'organization': 'Milwaukee Brewers', 'age': 19},
            {'name': 'Ethan Salas', 'position': 'C', 'organization': 'San Diego Padres', 'age': 17},
            {'name': 'Jackson Chourio', 'position': 'OF', 'organization': 'Milwaukee Brewers', 'age': 19},
            {'name': 'Paul Skenes', 'position': 'P', 'organization': 'Pittsburgh Pirates', 'age': 21},
            {'name': 'Dylan Crews', 'position': 'OF', 'organization': 'Washington Nationals', 'age': 21},
            {'name': 'Roki Sasaki', 'position': 'P', 'organization': 'Los Angeles Dodgers', 'age': 23},
        ]

        prospects = []
        for data in prospect_data:
            prospect = Prospect.objects.create(
                **data,
                created_by=test_teams[0],  # First team creates all prospects
                notes=f'Test prospect created for development'
            )
            prospects.append(prospect)
            self.stdout.write(f'Created prospect: {prospect.name}')

        # Create some active bids
        if options['fast_bids']:
            # Create bids with 5-minute expiration for testing
            bid_duration = timedelta(minutes=5)
            self.stdout.write('Creating test bids with 5-minute expiration...')
        else:
            bid_duration = timedelta(hours=24)
            self.stdout.write('Creating test bids with 24-hour expiration...')

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
                status='active'
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
                f'For fast testing, run: python manage.py create_test_data --fast-bids'
            )
        ) 