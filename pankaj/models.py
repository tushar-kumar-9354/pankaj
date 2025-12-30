
# models.py
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import uuid

class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('FEMA', 'FEMA'),
        ('SEBI', 'SEBI'),
        ('Corporate Law', 'Corporate Law'),
        ('Fundraising', 'Fundraising'),
        ('Startups', 'Startups'),
        ('Compliance', 'Compliance'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    date_published = models.DateTimeField(default=timezone.now)
    read_time = models.IntegerField(default=5)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            
            # Check if slug exists, add counter if it does
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        if not self.excerpt and self.content:
            self.excerpt = self.content[:300] + "..."
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date_published']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"


class Testimonial(models.Model):
    INDUSTRY_CHOICES = [
        ('Technology', 'Technology'),
        ('Manufacturing', 'Manufacturing'),
        ('Finance', 'Finance'),
        ('Startups', 'Startups'),
        ('Healthcare', 'Healthcare'),
        ('Retail', 'Retail'),
        ('Pharmaceuticals', 'Pharmaceuticals'),
    ]

    client_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    content = models.TextField(blank=True)

    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])

    client_image = models.ImageField(upload_to='testimonial_images/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    video = models.FileField(
        upload_to="testimonials/videos/",
        blank=True,
        null=True
    )

    video_url = models.URLField(
        blank=True,
        null=True
    )

    def get_video_source(self):
        if self.video:
            return self.video.url
        return self.video_url
    video_thumbnail = models.ImageField(
        upload_to='testimonial_videos/',
        blank=True,
        null=True,
        help_text="Thumbnail image for video testimonial"
    )

    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    services = models.CharField(max_length=200, blank=True)

    def is_video(self):
        return bool(self.video_url)
    def get_service_tags(self):
        """Convert comma-separated services to list"""
        if self.services:
            return [service.strip() for service in self.services.split(',') if service.strip()]
        return []

    def __str__(self):
        return f"{self.client_name} - {self.company}"

    class Meta:
        ordering = ['-date_added']

# models.py - Add this new model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class TestimonialSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    INDUSTRY_CHOICES = [
        ('Technology', 'Technology'),
        ('Manufacturing', 'Manufacturing'),
        ('Finance', 'Finance'),
        ('Startups', 'Startups'),
        ('Healthcare', 'Healthcare'),
        ('Retail', 'Retail'),
        ('Pharmaceuticals', 'Pharmaceuticals'),
        ('Other', 'Other'),
    ]
    
    # User details
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Company details
    company_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
    
    # Testimonial content
    testimonial_text = models.TextField()
    rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Services used (comma-separated)
    services_used = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated list of services used"
    )
    
    # Optional media
    profile_picture = models.ImageField(
        upload_to='testimonial_submissions/profiles/',
        blank=True,
        null=True
    )
    
    # Admin fields
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    admin_notes = models.TextField(blank=True)
    submitted_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    
    # Link to approved testimonial (if approved and converted)
    approved_testimonial = models.OneToOneField(
        'Testimonial',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='submission'
    )
    
    def __str__(self):
        return f"{self.full_name} - {self.company_name} ({self.status})"
    
    class Meta:
        ordering = ['-submitted_date']
        verbose_name = "Testimonial Submission"
        verbose_name_plural = "Testimonial Submissions"


# Add to models.py
from django.db import models
import uuid
from django.utils import timezone
# In models.py, update the ConsultationBooking model
class ConsultationBooking(models.Model):
    MODE_CHOICES = [
        ('video', 'Video Call'),
        ('phone', 'Phone Call'),
        ('in_person', 'In-person'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Booking Information
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    duration = models.CharField(max_length=20, choices=[
        ('30-min', '30 Minutes'),
        ('45-min', '45 Minutes'),
        ('60-min', '60 Minutes'),
    ])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Client Information
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=200, blank=True, null=True)
    designation = models.CharField(max_length=200, blank=True, null=True)
    
    # Consultation Details
    topic = models.TextField()
    documents = models.FileField(upload_to='consultation_docs/', blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    
    # Admin Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)  # ADD THIS
    cancellation_reason = models.TextField(blank=True, null=True)  # ADD THIS
    is_paid = models.BooleanField(default=False)
    pending_at = models.DateTimeField(blank=True, null=True)    # ADD THIS
    completed_at = models.DateTimeField(blank=True, null=True)
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    
    # Newsletter consent
    newsletter_consent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.appointment_date} {self.appointment_time}"
    
    class Meta:
        ordering = ['-appointment_date', 'appointment_time']
        verbose_name = "Consultation Booking"
        verbose_name_plural = "Consultation Bookings"
    
    # ADD THIS METHOD
    def is_cancellable(self):
        """Check if booking can be cancelled"""
        if self.status == 'cancelled':
            return False
        
        appointment_datetime = timezone.make_aware(
            datetime.combine(self.appointment_date, self.appointment_time)
        )
        
        # Allow cancellation up to 24 hours before appointment
        time_until_appointment = appointment_datetime - timezone.now()
        return time_until_appointment.total_seconds() > 86400  # 24 hours in seconds
    
    def save(self, *args, **kwargs):
        # Update timestamps when status changes
        if not self.pk:  # New booking
            self.pending_at = timezone.now()
        
        # Call parent save first to ensure we have an ID
        super().save(*args, **kwargs)
# Update the AvailableSlot model
class AvailableSlot(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    DURATION_CHOICES = [
        ('30', '30 Minutes'),
        ('45', '45 Minutes'),
        ('60', '60 Minutes'),
    ]
    
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES, default='60')
    max_bookings = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_day_display()} {self.start_time} - {self.end_time} ({self.get_duration_display()})"
    
    class Meta:
        ordering = ['day', 'start_time']
class BookedSlot(models.Model):
    slot = models.ForeignKey(AvailableSlot, on_delete=models.CASCADE, related_name='bookings')
    booking = models.ForeignKey(ConsultationBooking, on_delete=models.CASCADE)
    date = models.DateField()
    
    class Meta:
        unique_together = ['slot', 'date']

# Add to models.py
from datetime import datetime, timedelta
import uuid

class TimeSlotManager:
    """Manager to handle time slot logic"""
    
    @staticmethod
    def get_available_times(date_obj, duration_minutes):
        """Get all available start times for a given date and duration"""
        # Convert duration to timedelta
        duration_td = timedelta(minutes=duration_minutes)
        
        # Working hours: 9 AM to 5 PM (with 15 min buffer between appointments)
        start_hour = 9
        end_hour = 17
        
        # Get all bookings for this date
        bookings = ConsultationBooking.objects.filter(
            appointment_date=date_obj
        ).order_by('appointment_time')
        
        # Generate all possible start times (every 15 minutes)
        possible_slots = []
        current_time = datetime.combine(date_obj, datetime.min.time())
        current_time = current_time.replace(hour=start_hour, minute=0)
        end_time = current_time.replace(hour=end_hour, minute=0)
        
        while current_time.time() <= end_time.time():
            slot_end = current_time + duration_td
            
            # Check if slot ends before working hours end
            if slot_end.time() <= end_time.time():
                # Check if this slot overlaps with any existing booking
                is_available = True
                
                for booking in bookings:
                    booking_start = datetime.combine(date_obj, booking.appointment_time)
                    booking_duration = timedelta(minutes=int(booking.duration.replace('-min', '')))
                    booking_end = booking_start + booking_duration + timedelta(minutes=15)  # Add buffer
                    
                    # Check for overlap
                    if (current_time < booking_end and slot_end > booking_start):
                        is_available = False
                        break
                
                if is_available:
                    possible_slots.append({
                        'start_time': current_time.time(),
                        'end_time': slot_end.time(),
                        'display': f"{current_time.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}"
                    })
            
            # Increment by 15 minutes for next slot
            current_time += timedelta(minutes=15)
        
        return possible_slots
    
    @staticmethod
    def is_time_available(date_obj, start_time, duration_minutes):
        """Check if a specific time is available"""
        duration_td = timedelta(minutes=duration_minutes)
        requested_start = datetime.combine(date_obj, start_time)
        requested_end = requested_start + duration_td
        
        # Get all bookings for this date
        bookings = ConsultationBooking.objects.filter(
            appointment_date=date_obj
        ).exclude(status='cancelled')
        
        for booking in bookings:
            booking_start = datetime.combine(date_obj, booking.appointment_time)
            booking_duration = timedelta(minutes=int(booking.duration.replace('-min', '')))
            booking_end = booking_start + booking_duration + timedelta(minutes=15)  # Add buffer
            
            # Check for overlap
            if (requested_start < booking_end and requested_end > booking_start):
                return False
        
        return True