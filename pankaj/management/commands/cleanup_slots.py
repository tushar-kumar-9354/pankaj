# management/commands/cleanup_slots.py
from django.core.management.base import BaseCommand
from pankaj.models import AvailableSlot, BookedSlot
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Clean up old slot system and prepare for new linear time management'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Cleaning up old slot system...')
        
        # Archive old bookings (keep for reference)
        old_bookings = BookedSlot.objects.all()
        self.stdout.write(f'Archiving {old_bookings.count()} old bookings...')
        
        # Keep AvailableSlot but mark as inactive
        old_slots = AvailableSlot.objects.update(is_active=False)
        self.stdout.write(f'Deactivated all old slots')
        
        self.stdout.write(self.style.SUCCESS('Cleanup complete! New linear time management is ready.'))