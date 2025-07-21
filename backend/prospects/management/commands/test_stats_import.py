from django.core.management.base import BaseCommand
from prospects.models import Prospect
from prospects.services import get_baseball_data_service


class Command(BaseCommand):
    help = 'Test the baseball stats import functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--player-name',
            type=str,
            help='Test with a specific player name'
        )
        parser.add_argument(
            '--birth-year',
            type=int,
            help='Player birth year (for more accurate matching)'
        )
        parser.add_argument(
            '--birth-month',
            type=int,
            help='Player birth month (for more accurate matching)'
        )
        parser.add_argument(
            '--birth-day',
            type=int,
            help='Player birth day (for more accurate matching)'
        )
        parser.add_argument(
            '--pitching',
            action='store_true',
            help='Get pitching stats'
        )

    def handle(self, *args, **options):
        baseball_service = get_baseball_data_service()
        
        if options['player_name']:
            # Test with a specific player name
            player_name = options['player_name']
            birth_year = options.get('birth_year')
            birth_month = options.get('birth_month')
            birth_day = options.get('birth_day')
            
            self.stdout.write(f"Testing MLB stats for: {player_name}")
            if birth_year:
                self.stdout.write(f"With birth date: {birth_year}-{birth_month or '??'}-{birth_day or '??'}")
            
            # Use the search_player method directly to test the full pipeline
            players = baseball_service.load_chadwick_data()
            player_data = baseball_service.search_player(
                player_name, 
                players,
                birth_year=birth_year,
                birth_month=birth_month,
                birth_day=birth_day,
                pitching=options['pitching']
            )
            
            if player_data:
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"MLB Stats for {player_name}:\n"
                        f"  At Bats or Innings Pitched: {player_data}\n Type: {type(player_data)}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Could not find player: {player_name}")
                )
        else:
            # Test with a sample prospect
            self.stdout.write("Testing with a sample prospect...")
            
            sample_prospect = Prospect.objects.first()
            if sample_prospect:
                self.stdout.write(f"Testing: {sample_prospect.name}")
                try:
                    # Try to extract birth date from prospect if available
                    birth_year = None
                    if hasattr(sample_prospect, 'date_of_birth') and sample_prospect.date_of_birth:
                        birth_year = sample_prospect.date_of_birth.year
                        birth_month = sample_prospect.date_of_birth.month
                        birth_day = sample_prospect.date_of_birth.day
                        self.stdout.write(f"Using birth date: {birth_year}-{birth_month}-{birth_day}")
                    else:
                        birth_month = None
                        birth_day = None
                    
                    players = baseball_service.load_chadwick_data()
                    player_data = baseball_service.search_player(
                        sample_prospect.name,
                        players,
                        birth_year=birth_year,
                        birth_month=birth_month,
                        birth_day=birth_day,
                        pitching=sample_prospect.position == 'P'
                    )
                    
                    if player_data:
                        self.stdout.write(f"Player data: {player_data}, type: {type(player_data)}")

                        self.stdout.write(
                            f"  Current: {sample_prospect.at_bats} AB, {sample_prospect.innings_pitched} IP\n" 
                            f"  Updated: {player_data} AB or IP"
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"  Could not find player: {sample_prospect.name}")
                        )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  Error: {e}")
                    )
            else:
                self.stdout.write("No prospects found in database") 