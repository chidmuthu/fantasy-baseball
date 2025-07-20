from django.core.management.base import BaseCommand
from bidding.models import Bid


class Command(BaseCommand):
    help = 'Check and complete expired bids'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be completed without actually completing bids',
        )

    def handle(self, *args, **options):
        from django.utils import timezone
        
        # Find bids that have expired (expires_at is in the past)
        expired_bids = Bid.objects.filter(
            status='active',
            expires_at__lt=timezone.now()
        )
        
        if not expired_bids.exists():
            self.stdout.write(
                self.style.SUCCESS('No expired bids found.')
            )
            return
        
        self.stdout.write(f'Found {expired_bids.count()} expired bids.')
        
        if options['dry_run']:
            self.stdout.write('DRY RUN - Would complete the following bids:')
            for bid in expired_bids:
                self.stdout.write(
                    f'  - {bid.prospect.name} (won by {bid.current_bidder.name} for {bid.current_bid} POM)'
                )
            return
        
        completed_count = 0
        for bid in expired_bids:
            try:
                if bid.complete_bid():
                    completed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Completed bid for {bid.prospect.name} - {bid.current_bidder.name} wins for {bid.current_bid} POM'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Failed to complete bid for {bid.prospect.name}'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error completing bid for {bid.prospect.name}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully completed {completed_count} bids.')
        ) 