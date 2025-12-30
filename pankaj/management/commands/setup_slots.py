# Update your setup_slots.py command
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time, timedelta
from pankaj.models import AvailableSlot
from datetime import datetime

class Command(BaseCommand):
    help = 'Sets up initial consultation time slots with different durations'
    
    def handle(self, *args, **kwargs):
        # Define working hours
        slots = []
        
        # Monday to Friday: 9 AM to 6 PM
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            # 30-minute slots
            for hour in range(9, 18):  # 9 AM to 6 PM
                for minute in [0, 30]:
                    if hour == 17 and minute == 30:  # Skip 5:30 PM slot (ends at 6 PM)
                        continue
                    slots.append({
                        'day': day,
                        'start_time': time(hour, minute),
                        'duration': '30',
                        'max_bookings': 3,
                    })
            
            # 45-minute slots (at specific times)
            for time_slot in [(9,0), (11,0), (14,0), (16,0)]:
                slots.append({
                    'day': day,
                    'start_time': time(time_slot[0], time_slot[1]),
                    'duration': '45',
                    'max_bookings': 2,
                })
            
            # 60-minute slots
            for hour in range(9, 17):  # 9 AM to 5 PM
                slots.append({
                    'day': day,
                    'start_time': time(hour, 0),
                    'duration': '60',
                    'max_bookings': 1,
                })
        
        # Saturday: 10 AM to 4 PM
        for day in ['saturday']:
            # 30-minute slots
            for hour in range(10, 16):  # 10 AM to 4 PM
                for minute in [0, 30]:
                    if hour == 15 and minute == 30:  # Skip 3:30 PM slot
                        continue
                    slots.append({
                        'day': day,
                        'start_time': time(hour, minute),
                        'duration': '30',
                        'max_bookings': 2,
                    })
            
            # 45-minute slots
            for time_slot in [(10,0), (12,30), (14,0)]:
                slots.append({
                    'day': day,
                    'start_time': time(time_slot[0], time_slot[1]),
                    'duration': '45',
                    'max_bookings': 2,
                })
            
            # 60-minute slots
            for hour in range(10, 15):  # 10 AM to 3 PM
                slots.append({
                    'day': day,
                    'start_time': time(hour, 0),
                    'duration': '60',
                    'max_bookings': 1,
                })
        
        # Create slots with calculated end times
        created_count = 0
        for slot_data in slots:
            start_time = slot_data['start_time']
            duration = int(slot_data['duration'])
            
            # Calculate end time
            start_datetime = datetime.combine(datetime.today(), start_time)
            end_datetime = start_datetime + timedelta(minutes=duration)
            end_time = end_datetime.time()
            
            slot, created = AvailableSlot.objects.get_or_create(
                day=slot_data['day'],
                start_time=start_time,
                duration=slot_data['duration'],
                defaults={
                    'end_time': end_time,
                    'max_bookings': slot_data['max_bookings'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully set up {created_count} consultation slots with various durations')
        )
        
        # Show summary by duration
        for duration in ['30', '45', '60']:
            count = AvailableSlot.objects.filter(duration=duration).count()
            self.stdout.write(f'  - {duration}-minute slots: {count}')