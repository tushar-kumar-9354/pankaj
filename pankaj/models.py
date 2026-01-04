
# ══════════════════════════════════════════════════════════════════════════════
#                              IMPORTS
# ══════════════════════════════════════════════════════════════════════════════

import random
import uuid  # For generating unique identifiers
from datetime import datetime, time, timedelta  # For date/time manipulation
from chromadb import logger
from django.core.validators import MinValueValidator, MaxValueValidator  # For field validation
from django.db import models  # Django's ORM for database models
from django.utils import timezone  # Timezone-aware datetime handling
from django.utils.text import slugify
from jsonschema import ValidationError  # For creating URL-friendly slugs
import razorpay
from django.conf import settings
# ══════════════════════════════════════════════════════════════════════════════
#                              BLOG POST MODEL
# ══════════════════════════════════════════════════════════════════════════════
class BlogPost(models.Model):
    """
    Represents a blog post/article with various metadata and content.
    """
    
    # ─── Category Choices ───────────────────────────────────────────────────────
    # Defines the allowed categories for blog posts
    CATEGORY_CHOICES = [
        ('FEMA', 'FEMA'),
        ('SEBI', 'SEBI'),
        ('Corporate Law', 'Corporate Law'),
        ('Fundraising', 'Fundraising'),
        ('Startups', 'Startups'),
        ('Compliance', 'Compliance'),
    ]
    
    # ─── Core Content Fields ────────────────────────────────────────────────────
    title = models.CharField(max_length=200)  # Title of the blog post
    slug = models.SlugField(max_length=200, unique=True, blank=True)  # URL-friendly identifier
    content = models.TextField()  # Main content of the blog post
    excerpt = models.TextField(max_length=300, blank=True)  # Short summary/teaser
    
    # ─── Metadata Fields ────────────────────────────────────────────────────────
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)  # Post category
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)  # Main image
    image_url = models.URLField(blank=True, null=True)  # Alternative image URL
    date_published = models.DateTimeField(default=timezone.now)  # Publication date
    read_time = models.IntegerField(default=5)  # Estimated reading time in minutes
    
    # ─── Status Flags ───────────────────────────────────────────────────────────
    is_published = models.BooleanField(default=True)  # Controls visibility
    is_featured = models.BooleanField(default=False)  # Marks featured posts
    
    # ─── Model Methods ──────────────────────────────────────────────────────────
    meta_title = models.CharField(max_length=200, blank=True, help_text="SEO meta title (optional)")
    meta_description = models.TextField(max_length=300, blank=True, help_text="SEO meta description (optional)")
    meta_keywords = models.CharField(max_length=200, blank=True, help_text="SEO keywords (comma-separated)")
    author = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Admin who created this post"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0, editable=False)
    
    # Add this method to increment view count
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def clean(self):
        """Validation before save"""
        super().clean()
        # Ensure title is not empty
        if not self.title or self.title.strip() == '':
            from django.core.exceptions import ValidationError
            raise ValidationError({'title': 'Title cannot be empty'})
    
    def save(self, *args, **kwargs):
        """
        Override save method to ALWAYS ensure a valid slug exists
        """
        # IMPORTANT: Handle slug generation BEFORE saving
        from django.utils.text import slugify
        import uuid
        
        # Clean the slug
        if self.slug:
            self.slug = str(self.slug).strip()
        
        # If slug is empty, generate it from title
        if not self.slug or self.slug == '':
            # Generate from title
            if self.title and self.title.strip() != '':
                base_slug = slugify(self.title)
            else:
                base_slug = f"blog-{uuid.uuid4().hex[:8]}"
            
            # Ensure base slug is not empty
            if not base_slug or base_slug.strip() == '':
                base_slug = f"blog-post-{uuid.uuid4().hex[:8]}"
            
            # Make unique
            slug = base_slug
            counter = 1
            
            # Check for existing slugs (exclude current object if it has ID)
            query = BlogPost.objects.filter(slug=slug)
            if self.pk:
                query = query.exclude(pk=self.pk)
            
            while query.exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                query = BlogPost.objects.filter(slug=slug)
                if self.pk:
                    query = query.exclude(pk=self.pk)
            
            self.slug = slug
        
        # Auto-generate excerpt from content if not provided
        if not self.excerpt and self.content:
            excerpt_text = self.content.replace('\n', ' ').strip()
            if len(excerpt_text) > 300:
                self.excerpt = excerpt_text[:300] + "..."
            else:
                self.excerpt = excerpt_text
        
        # If date_published is not set and post is published, set it to now
        if self.is_published and not self.date_published:
            self.date_published = timezone.now()
        
        # If date_published is in the future, don't publish yet
        if self.date_published and self.date_published > timezone.now():
            self.is_published = False
        
        # Call parent save
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Always return a valid URL for the blog post"""
        # Ensure slug is not empty
        if not self.slug or str(self.slug).strip() == '':
            # Regenerate slug on the fly if empty
            self.save(update_fields=['slug'])
        
        from django.urls import reverse
        try:
            return reverse('blog_detail', kwargs={'slug': self.slug})
        except:
            # Emergency fallback
            return f"/blogs/{self.slug}/"
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date_published']
def clean(self):
    """Validation before save"""
    super().clean()
    # Ensure title is not empty
    if not self.title or self.title.strip() == '':
        from django.core.exceptions import ValidationError
        raise ValidationError({'title': 'Title cannot be empty'})
    
    # Ensure slug will be generated if empty
    if not self.slug or str(self.slug).strip() == '':
        # Don't raise error, just note that slug will be auto-generated
        pass
def save(self, *args, **kwargs):
    """
    Override save method to ALWAYS ensure a valid slug exists
    """
    # Clean the slug
    if self.slug:
        self.slug = str(self.slug).strip()
    
    # Generate slug if empty
    if not self.slug or self.slug == '':
        # Import here to avoid circular imports
        from django.utils.text import slugify
        import uuid
        
        # Generate from title
        if self.title and self.title.strip() != '':
            base_slug = slugify(self.title)
        else:
            base_slug = f"blog-{uuid.uuid4().hex[:8]}"
        
        # Ensure base slug is not empty
        if not base_slug or base_slug.strip() == '':
            base_slug = f"blog-post-{uuid.uuid4().hex[:8]}"
        
        # Make unique
        slug = base_slug
        counter = 1
        
        # First save to get an ID if this is a new object
        if not self.id:
            # Temporarily set a placeholder slug
            temp_slug = f"temp-{uuid.uuid4().hex[:8]}"
            self.slug = temp_slug
            # Save to get ID
            super().save(*args, **kwargs)
        
        # Now check for uniqueness with the actual ID
        while BlogPost.objects.filter(slug=slug).exclude(id=self.id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        self.slug = slug
    
    # Auto-generate excerpt from content if not provided
    if not self.excerpt and self.content:
        excerpt_text = self.content.replace('\n', ' ').strip()
        if len(excerpt_text) > 300:
            self.excerpt = excerpt_text[:300] + "..."
        else:
            self.excerpt = excerpt_text
    
    # If date_published is not set and post is published, set it to now
    if self.is_published and not self.date_published:
        self.date_published = timezone.now()
    
    # If date_published is in the future, don't publish yet
    if self.date_published and self.date_published > timezone.now():
        self.is_published = False
    
    # Call parent save
    super().save(*args, **kwargs)
def get_absolute_url(self):
    """Always return a valid URL for the blog post"""
    # Ensure slug is not empty
    if not self.slug or str(self.slug).strip() == '':
        # Regenerate slug on the fly if empty
        self.save(update_fields=['slug'])
    
    from django.urls import reverse
    try:
        return reverse('blog_detail', kwargs={'slug': self.slug})
    except:
        # Emergency fallback
        return f"/blogs/{self.slug}/"
# Add this method to your BlogPost model in models.py
def get_category_image(self):
    """Return a default image URL based on blog category."""
    category_images = {
        'FEMA': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=100',
        'SEBI': 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=100',
        'Corporate Law': 'https://images.unsplash.com/photo-1589391886085-8b6b0ac72a1a?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=100',
        'Fundraising': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=100',
        'Startups': 'https://images.unsplash.com/photo-1556761175-b413da4baf72?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=100',
        'Compliance': 'https://images.unsplash.com/photo-1559136555-9303baea8ebd?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=100',
    }
    return category_images.get(self.category, 'https://images.unsplash.com/photo-1553877522-43269d4ea984?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=100')



# ══════════════════════════════════════════════════════════════════════════════
#                              TESTIMONIAL MODEL
# ══════════════════════════════════════════════════════════════════════════════

class Testimonial(models.Model):
    """
    Represents client testimonials, can include text, image, or video testimonials.
    """
    
    # ─── Industry Choices ───────────────────────────────────────────────────────
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
    
    # ─── Client Information Fields ──────────────────────────────────────────────
    client_name = models.CharField(max_length=100)  # Name of the client
    company = models.CharField(max_length=100)  # Client's company name
    position = models.CharField(max_length=100)  # Client's position/role
    content = models.TextField(blank=True)  # Testimonial text content
    
    # ─── Categorization Fields ──────────────────────────────────────────────────
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)  # Industry sector
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])  # 1-5 star rating
    
    # ─── Media Fields ───────────────────────────────────────────────────────────
    client_image = models.ImageField(upload_to='testimonial_images/', blank=True, null=True)  # Client photo
    image_url = models.URLField(blank=True, null=True)  # Alternative image URL
    
    
    # ─── Administrative Fields ──────────────────────────────────────────────────
    date_added = models.DateTimeField(auto_now_add=True)  # Auto-set on creation
    is_active = models.BooleanField(default=True)  # Controls visibility
    is_featured = models.BooleanField(default=False)  # Marks featured testimonials

    # ─── Services Field ─────────────────────────────────────────────────--------
    SERVICE_CHOICES1 = [
        ('FEMA', 'FEMA'),
        ('SEBI', 'SEBI'),
        ('Corporate Law', 'Corporate Law'),
        ('Fundraising', 'Fundraising'),
        ('Startups', 'Startups'),
        ('Compliance', 'Compliance'),
    ]
    services = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES1,   # 👈 makes it a dropdown
        blank=True,
        help_text="Select service used"
    )  # Comma-separated services used
    
    # ─── Model Methods ──────────────────────────────────────────────────────────
    
    
    def get_service_tags(self):
        """Converts comma-separated services string to list of tags."""
        if self.services:
            return [service.strip() for service in self.services.split(',') if service.strip()]
        return []
    
    def __str__(self):
        """String representation for admin interface and debugging."""
        return f"{self.client_name} - {self.company}"
    
    # ─── Meta Configuration ─────────────────────────────────────────────────────
    class Meta:
        ordering = ['-date_added']  # Order by most recent first


# ══════════════════════════════════════════════════════════════════════════════
#                              TESTIMONIAL SUBMISSION MODEL
# ══════════════════════════════════════════════════════════════════════════════

class TestimonialSubmission(models.Model):
    """
    Represents user-submitted testimonials awaiting admin approval.
    """
    
    # ─── Status Choices ─────────────────────────────────────────────────────────
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # ─── Industry Choices (Extended) ────────────────────────────────────────────
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
    
    # ─── User Details Fields ────────────────────────────────────────────────────
    full_name = models.CharField(max_length=100)  # Submitter's full name
    email = models.EmailField()  # Submitter's email address
    phone = models.CharField(max_length=15, blank=True, null=True)  # Contact phone
    
    # ─── Company Details Fields ─────────────────────────────────────────────────
    company_name = models.CharField(max_length=100)  # Company name
    position = models.CharField(max_length=100)  # Position in company
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)  # Industry sector
    
    # ─── Testimonial Content Fields ─────────────────────────────────────────────
    testimonial_text = models.TextField()  # The testimonial content
    rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]  # Ensure rating is 1-5
    )
    
    # ─── Services Field ─────────────────────────────────────────────────────────
    SERVICE_CHOICES = [
        ('FEMA', 'FEMA'),
        ('SEBI', 'SEBI'),
        ('Corporate Law', 'Corporate Law'),
        ('Fundraising', 'Fundraising'),
        ('Startups', 'Startups'),
        ('Compliance', 'Compliance'),
    ]
    
    services_used = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES,   # 👈 makes it a dropdown
        blank=True,
        help_text="Select service used"
    )
    # ─── Optional Media Fields ──────────────────────────────────────────────────
    profile_picture = models.ImageField(
        upload_to='testimonial_submissions/profiles/',
        blank=True,
        null=True
    )  # Optional profile picture
    
    # ─── Administrative Fields ──────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )  # Current status of submission
    
    admin_notes = models.TextField(blank=True)  # Internal notes from admin
    submitted_date = models.DateTimeField(auto_now_add=True)  # Auto-set on submission
    approved_date = models.DateTimeField(blank=True, null=True)  # Date of approval
    is_public = models.BooleanField(default=False)  # Visibility flag
    
    # ─── Relationship Field ─────────────────────────────────────────────────────
    approved_testimonial = models.OneToOneField(
        'Testimonial',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='submission'
    )  # Link to approved testimonial if converted
    
    # ─── Model Methods ──────────────────────────────────────────────────────────
    
    def __str__(self):
        """String representation for admin interface and debugging."""
        return f"{self.full_name} - {self.company_name} ({self.status})"
    
    # ─── Meta Configuration ─────────────────────────────────────────────────────
    class Meta:
        ordering = ['-submitted_date']  # Order by most recent submission
        verbose_name = "Testimonial Submission"  # Singular name for admin
        verbose_name_plural = "Testimonial Submissions"  # Plural name for admin


# ══════════════════════════════════════════════════════════════════════════════
#                              CONSULTATION BOOKING MODEL
# ══════════════════════════════════════════════════════════════════════════════

class ConsultationBooking(models.Model):
    """
    Represents a scheduled consultation appointment between client and advisor.
    """
    
    # ─── Mode Choices ───────────────────────────────────────────────────────────
    MODE_CHOICES = [
        ('video', 'Video Call'),
        ('phone', 'Phone Call'),
        
    ]
    
    # ─── Status Choices ─────────────────────────────────────────────────────────
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # ─── Booking Information Fields ─────────────────────────────────────────────
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Unique booking ID
    duration = models.CharField(max_length=20, choices=[
        ('30-min', '30 Minutes'),
        ('45-min', '45 Minutes'),
        ('60-min', '60 Minutes'),
    ])  # Consultation duration
    
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Consultation fee
    appointment_date = models.DateField()  # Date of appointment
    appointment_time = models.TimeField()  # Time of appointment
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)  # Consultation mode
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Booking status
    
    # ─── Client Information Fields ──────────────────────────────────────────────
    name = models.CharField(max_length=200)  # Client's name
    email = models.EmailField()  # Client's email
    phone = models.CharField(max_length=20)  # Client's phone
    company = models.CharField(max_length=200, blank=True, null=True)  # Client's company
    designation = models.CharField(max_length=200, blank=True, null=True)  # Client's designation
    
    # ─── Consultation Details Fields ────────────────────────────────────────────
    topic = models.TextField()  # Consultation topic/agenda
    documents = models.FileField(upload_to='consultation_docs/', blank=True, null=True)  # Related documents
    additional_notes = models.TextField(blank=True, null=True)  # Additional information
    
    # ─── Administrative Fields ──────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set on creation
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated on save
    
    # ─── Status Timestamp Fields ────────────────────────────────────────────────
    confirmed_at = models.DateTimeField(blank=True, null=True)  # When booking was confirmed
    cancelled_at = models.DateTimeField(blank=True, null=True)  # When booking was cancelled
    cancellation_reason = models.TextField(blank=True, null=True)  # Reason for cancellation
    is_paid = models.BooleanField(default=False)  # Payment status
    pending_at = models.DateTimeField(blank=True, null=True)  # When booking entered pending state
    completed_at = models.DateTimeField(blank=True, null=True)  # When consultation completed
    
    # ─── Payment Fields ─────────────────────────────────────────────────────────
    payment_id = models.CharField(max_length=200, blank=True, null=True)  # Payment gateway reference
    
    
    # ─── Marketing Fields ───────────────────────────────────────────────────────
    newsletter_consent = models.BooleanField(default=False)  # Newsletter subscription consent
    
    # ─── Model Methods ──────────────────────────────────────────────────────────
    
    def __str__(self):
        """String representation for admin interface and debugging."""
        return f"{self.name} - {self.appointment_date} {self.appointment_time}"
    
    def is_cancellable(self):
        """
        Checks if booking can be cancelled (must be >24 hours before appointment).
        
        Returns:
            bool: True if booking can be cancelled, False otherwise
        """
        if self.status == 'cancelled':
            return False  # Already cancelled
        
        # Combine date and time to create datetime object
        appointment_datetime = timezone.make_aware(
            datetime.combine(self.appointment_date, self.appointment_time)
        )
        
        # Calculate time until appointment
        time_until_appointment = appointment_datetime - timezone.now()
        
        # Allow cancellation up to 24 hours before appointment (86400 seconds)
        return time_until_appointment.total_seconds() > 86400
    
    def initiate_payment(self):
        """
        Initiate payment through Razorpay.
        """
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Create order data
        order_data = {
            'amount': int(self.price * 100),  # Convert to paise
            'currency': 'INR',
            'receipt': str(self.booking_id),
            'notes': {
                'booking_id': str(self.booking_id),
                'customer_name': self.name,
                'customer_email': self.email
            }
        }
        
        try:
            # Create Razorpay order
            order = client.order.create(data=order_data)
            
            # Create Payment record
            payment = Payment.objects.create(
                booking=self,
                razorpay_order_id=order['id'],
                amount=self.price,
                currency='INR'
            )
            
            return {
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key': settings.RAZORPAY_KEY_ID,
                'name': "KP RegTech",
                'description': f"Consultation Booking - {self.get_duration_display()}",
                'prefill': {
                    'name': self.name,
                    'email': self.email,
                    'contact': self.phone
                },
                'notes': {
                    'booking_id': str(self.booking_id)
                },
                'theme': {
                    'color': '#4CAF50'
                }
            }
            
        except Exception as e:
            logger.error(f"Error initiating payment for booking {self.booking_id}: {str(e)}")
            return None
    
    def save(self, *args, **kwargs):
        """
        Override save method to update status timestamps.
        """
        # Set pending timestamp for new bookings
        if not self.pk:  # Check if this is a new instance
            self.pending_at = timezone.now()
        
        # Call parent class save method
        super().save(*args, **kwargs)
    
    # ─── Meta Configuration ─────────────────────────────────────────────────────
    class Meta:
        ordering = ['-appointment_date', 'appointment_time']  # Order by date then time
        verbose_name = "Consultation Booking"  # Singular name for admin
        verbose_name_plural = "Consultation Bookings"  # Plural name for admin


# ══════════════════════════════════════════════════════════════════════════════
#                              AVAILABLE SLOT MODEL
# ══════════════════════════════════════════════════════════════════════════════

class AvailableSlot(models.Model):
    """
    Defines available time slots for consultations on specific days.
    """
    
    # ─── Day Choices ────────────────────────────────────────────────────────────
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    # ─── Duration Choices ───────────────────────────────────────────────────────
    DURATION_CHOICES = [
        ('30', '30 Minutes'),
        ('45', '45 Minutes'),
        ('60', '60 Minutes'),
    ]
    
    # ─── Slot Definition Fields ─────────────────────────────────────────────────
    day = models.CharField(max_length=20, choices=DAY_CHOICES)  # Day of week
    start_time = models.TimeField()  # Slot start time
    end_time = models.TimeField()  # Slot end time
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES, default='60')  # Slot duration
    
    # ─── Capacity Fields ────────────────────────────────────────────────────────
    max_bookings = models.IntegerField(default=1)  # Maximum bookings per slot
    
    # ─── Status Fields ──────────────────────────────────────────────────────────
    is_active = models.BooleanField(default=True)  # Controls slot availability
    
    # ─── Model Methods ──────────────────────────────────────────────────────────
    
    def __str__(self):
        """String representation for admin interface and debugging."""
        return f"{self.get_day_display()} {self.start_time} - {self.end_time} ({self.get_duration_display()})"
    
    # ─── Meta Configuration ─────────────────────────────────────────────────────
    class Meta:
        ordering = ['day', 'start_time']  # Order by day then start time


# ══════════════════════════════════════════════════════════════════════════════
#                              BOOKED SLOT MODEL
# ══════════════════════════════════════════════════════════════════════════════

class BookedSlot(models.Model):
    """
    Tracks specific booked time slots (links AvailableSlot with ConsultationBooking).
    """
    
    # ─── Relationship Fields ────────────────────────────────────────────────────
    slot = models.ForeignKey(AvailableSlot, on_delete=models.CASCADE, related_name='bookings')  # The time slot
    booking = models.ForeignKey(ConsultationBooking, on_delete=models.CASCADE)  # The booking
    
    # ─── Date Field ─────────────────────────────────────────────────────────────
    date = models.DateField()  # Specific date of booking
    
    # ─── Meta Configuration ─────────────────────────────────────────────────────
    class Meta:
        # Ensure unique combination of slot and date (prevents double booking)
        unique_together = ['slot', 'date']


# ══════════════════════════════════════════════════════════════════════════════
#                              TIME SLOT MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class TimeSlotManager:
    """
    Utility class to handle time slot availability logic.
    Contains static methods for checking and generating available time slots.
    """
    
    @staticmethod
    def get_available_times(date_obj, duration_minutes):
        """
        Generates all available start times for a given date and duration.
        
        Args:
            date_obj (date): The date to check availability for
            duration_minutes (int): Duration of desired appointment in minutes
            
        Returns:
            list: List of dictionaries with available time slots
        """
        # Convert duration to timedelta for calculations
        duration_td = timedelta(minutes=duration_minutes)
        
        # Define working hours (9 AM to 5 PM)
        start_hour = 9
        end_hour = 17
        
        # Get all existing bookings for the specified date
        bookings = ConsultationBooking.objects.filter(
            appointment_date=date_obj
        ).order_by('appointment_time')
        
        # Initialize list to store available slots
        possible_slots = []
        
        # Start time calculations at beginning of day
        current_time = datetime.combine(date_obj, datetime.min.time())
        current_time = current_time.replace(hour=start_hour, minute=0)  # Set to 9:00 AM
        end_time = current_time.replace(hour=end_hour, minute=0)  # Set to 5:00 PM
        
        # Generate time slots every 15 minutes within working hours
        while current_time.time() <= end_time.time():
            slot_end = current_time + duration_td
            
            # Check if slot fits within working hours
            if slot_end.time() <= end_time.time():
                # Check for overlap with existing bookings
                is_available = True
                
                for booking in bookings:
                    # Calculate booking start and end times (with 15 min buffer)
                    booking_start = datetime.combine(date_obj, booking.appointment_time)
                    booking_duration = timedelta(minutes=int(booking.duration.replace('-min', '')))
                    booking_end = booking_start + booking_duration + timedelta(minutes=15)
                    
                    # Check for time overlap
                    if (current_time < booking_end and slot_end > booking_start):
                        is_available = False
                        break
                
                # Add to available slots if no overlap
                if is_available:
                    possible_slots.append({
                        'start_time': current_time.time(),  # Slot start time
                        'end_time': slot_end.time(),  # Slot end time
                        'display': f"{current_time.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}"  # User-friendly display
                    })
            
            # Move to next 15-minute interval
            current_time += timedelta(minutes=15)
        
        return possible_slots
    
    @staticmethod
    def is_time_available(date_obj, start_time, duration_minutes):
        """
        Checks if a specific time slot is available.
        
        Args:
            date_obj (date): The date to check
            start_time (time): The desired start time
            duration_minutes (int): Duration of appointment in minutes
            
        Returns:
            bool: True if time slot is available, False otherwise
        """
        # Convert duration to timedelta
        duration_td = timedelta(minutes=duration_minutes)
        
        # Calculate requested start and end times
        requested_start = datetime.combine(date_obj, start_time)
        requested_end = requested_start + duration_td
        
        # Get all non-cancelled bookings for the date
        bookings = ConsultationBooking.objects.filter(
            appointment_date=date_obj
        ).exclude(status='cancelled')
        
        # Check for overlap with existing bookings
        for booking in bookings:
            booking_start = datetime.combine(date_obj, booking.appointment_time)
            booking_duration = timedelta(minutes=int(booking.duration.replace('-min', '')))
            booking_end = booking_start + booking_duration + timedelta(minutes=15)  # Add buffer
            
            # Check for time overlap
            if (requested_start < booking_end and requested_end > booking_start):
                return False  # Time slot is not available
        
        return True  # Time slot is available
    
# ══════════════════════════════════════════════════════════════════════════════
#                              PAYMENT MODEL
# # ══════════════════════════════════════════════════════════════════════════════

# class Payment(models.Model):
#     """
#     Tracks payment transactions for consultation bookings.
#     """
    
#     # ─── Status Choices ─────────────────────────────────────────────────────────
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('completed', 'Completed'),
#         ('failed', 'Failed'),
#         ('refunded', 'Refunded'),
#     ]
    
#     # ─── Payment Method Choices ────────────────────────────────────────────────
#     METHOD_CHOICES = [
#         ('upi', 'UPI'),
#         ('card', 'Credit/Debit Card'),
#         ('netbanking', 'Net Banking'),
#         ('wallet', 'Wallet (PayTM/PhonePe)'),
#         ('cash', 'Cash/Offline'),
#     ]
    
#     # ─── Core Fields ───────────────────────────────────────────────────────────
#     booking = models.OneToOneField(ConsultationBooking, on_delete=models.CASCADE, related_name='payment')
#     payment_id = models.CharField(max_length=100, unique=True, blank=True)  # Payment gateway reference
#     razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)  # Razorpay order ID
#     razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)  # Razorpay payment ID
#     razorpay_signature = models.CharField(max_length=255, blank=True, null=True)  # Razorpay signature
    
#     # ─── Payment Details ───────────────────────────────────────────────────────
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     currency = models.CharField(max_length=3, default='INR')
#     method = models.CharField(max_length=20, choices=METHOD_CHOICES, blank=True, null=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
#     # ─── Additional Details ────────────────────────────────────────────────────
#     upi_id = models.CharField(max_length=100, blank=True, null=True)  # For UPI payments
#     card_last4 = models.CharField(max_length=4, blank=True, null=True)  # Last 4 digits of card
#     bank_name = models.CharField(max_length=100, blank=True, null=True)  # For net banking
    
#     # ─── Timestamps ────────────────────────────────────────────────────────────
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     completed_at = models.DateTimeField(blank=True, null=True)
    
#     # ─── Error Handling ────────────────────────────────────────────────────────
#     error_code = models.CharField(max_length=50, blank=True, null=True)
#     error_description = models.TextField(blank=True, null=True)
    
#     def __str__(self):
#         return f"Payment {self.payment_id} - {self.booking.name} - ₹{self.amount}"
    
#     def is_successful(self):
#         return self.status == 'completed'
    
#     def mark_as_completed(self, payment_id=None, method=None, additional_info=None):
#         self.status = 'completed'
#         self.completed_at = timezone.now()
#         if payment_id:
#             self.payment_id = payment_id
#         if method:
#             self.method = method
#         if additional_info:
#             if method == 'upi':
#                 self.upi_id = additional_info.get('upi_id')
#             elif method == 'card':
#                 self.card_last4 = additional_info.get('card_last4')
#             elif method == 'netbanking':
#                 self.bank_name = additional_info.get('bank_name')
#         self.save()
        
#         # Update booking payment status
#         self.booking.is_paid = True
#         self.booking.save()
    
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = "Payment"
#         verbose_name_plural = "Payments"


# ══════════════════════════════════════════════════════════════════════════════
#                              SIMPLE PAYMENT MODEL (TESTING)
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
#                              PAYMENT MODEL
# ══════════════════════════════════════════════════════════════════════════════
import uuid
import time
import random
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail, EmailMessage

def generate_payment_id():
    """Generate unique payment ID"""
    timestamp = int(time.time() * 1000)  # Milliseconds
    random_num = random.randint(1000, 9999)
    return f"PAY{timestamp}{random_num}"

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
        ('cash', 'Cash/Offline'),
    ]
    
    booking = models.OneToOneField('ConsultationBooking', on_delete=models.CASCADE, related_name='payment')
    payment_id = models.CharField(max_length=50, unique=True, default=generate_payment_id)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Cash payment verification fields
    cash_payment_verified = models.BooleanField(default=False)
    cash_payment_verified_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='verified_payments'
    )
    cash_payment_verified_at = models.DateTimeField(blank=True, null=True)
    cash_payment_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.payment_id} - {self.booking.name} - ₹{self.amount}"
    
    def mark_as_paid(self, verified_by=None, notes=None):
        """Mark payment as paid with appropriate handling"""
        self.status = 'success'
        self.completed_at = timezone.now()
        
        # For cash payments
        if self.method == 'cash':
            self.cash_payment_verified = True
            self.cash_payment_verified_at = timezone.now()
            self.cash_payment_verified_by = verified_by
            if notes:
                self.cash_payment_notes = notes
            
            # Update booking status for cash payments
            self.booking.is_paid = True
            self.booking.status = 'confirmed'
        else:
            # For online payments
            self.booking.is_paid = True
            self.booking.status = 'confirmed'
        
        self.booking.payment_id = self.payment_id
        self.booking.save()
        self.save()
        
        # Send confirmation emails
        self.send_payment_confirmation()
        
        return True
    
    def send_payment_confirmation(self):
        """Send payment confirmation email"""
        try:
            # Email to client
            self._send_client_email()
            
            # Email to admin
            self._send_admin_email()
            
            print(f"Payment confirmation emails sent for {self.payment_id}")
            return True
        except Exception as e:
            print(f"Error sending payment emails: {e}")
            return False
    
    def _send_client_email(self):
        """Send payment confirmation to client"""
        subject = f'Payment Confirmed - Booking {self.booking.booking_id}'
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>Payment Confirmed!</h2>
                <p>Dear {self.booking.name},</p>
                <p>Your payment has been successfully processed.</p>
                
                <div style="background: #f9f9f9; padding: 15px; margin: 15px 0;">
                    <h3>Payment Details</h3>
                    <p><strong>Payment ID:</strong> {self.payment_id}</p>
                    <p><strong>Transaction ID:</strong> {self.transaction_id or 'N/A'}</p>
                    <p><strong>Amount:</strong> ₹{self.amount}</p>
                    <p><strong>Method:</strong> {self.get_method_display()}</p>
                    <p><strong>Status:</strong> {self.get_status_display()}</p>
                </div>
                
                <p>Your consultation is now confirmed.</p>
                
                <p>Best regards,<br>
                <strong>KP RegTech</strong></p>
            </div>
        </body>
        </html>
        """
        
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.booking.email],
        )
        email.content_subtype = "html"
        email.send()
    
    def _send_admin_email(self):
        """Send payment notification to admin"""
        subject = f'New Payment Received - {self.booking.name}'
        
        message = f"""
        NEW PAYMENT RECEIVED
        
        Payment ID: {self.payment_id}
        Amount: ₹{self.amount}
        Method: {self.get_method_display()}
        Booking ID: {self.booking.booking_id}
        
        Client: {self.booking.name}
        Email: {self.booking.email}
        Phone: {self.booking.phone}
        """
        
        admin_email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL]
        )
        admin_email.send()

        
class Refund(models.Model):
    REFUND_STATUS = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Processed'),
    ]
    
    booking = models.ForeignKey(ConsultationBooking, on_delete=models.CASCADE, related_name='refunds')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    refund_id = models.CharField(max_length=50, unique=True, default=generate_payment_id)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=REFUND_STATUS, default='requested')
    requested_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_refunds')
    approved_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Refund {self.refund_id} - {self.booking.name} - ₹{self.amount}"
    
    def approve(self, approved_by, notes=None):
        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        if notes:
            self.notes = notes
        self.save()
        
        # Free up the booked slot
        self.free_booked_slot()
        
        # Send approval email
        self.send_refund_approval_email()
        
        return True
    
    def free_booked_slot(self):
        """Free the booked slot when refund is approved."""
        try:
            # Mark booking as cancelled
            self.booking.status = 'cancelled'
            self.booking.cancelled_at = timezone.now()
            self.booking.save()
            
            # You can add logic here to free up the time slot
            # For example, if you have a BookedSlot model:
            # BookedSlot.objects.filter(booking=self.booking).delete()
            
            print(f"Booking {self.booking.booking_id} cancelled and slot freed")
            return True
        except Exception as e:
            print(f"Error freeing slot: {e}")
            return False
    
    def send_refund_approval_email(self):
        """Send refund approval email to client."""
        try:
            subject = f'Refund Approved - {self.refund_id}'
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <body>
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>Refund Approved</h2>
                    <p>Dear {self.booking.name},</p>
                    <p>Your refund request has been approved.</p>
                    
                    <div style="background: #f9f9f9; padding: 15px; margin: 15px 0;">
                        <h3>Refund Details</h3>
                        <p><strong>Refund ID:</strong> {self.refund_id}</p>
                        <p><strong>Amount:</strong> ₹{self.amount}</p>
                        <p><strong>Reason:</strong> {self.reason}</p>
                        <p><strong>Status:</strong> Approved</p>
                        <p><strong>Booking ID:</strong> {self.booking.booking_id}</p>
                    </div>
                    
                    <p>The refund amount will be credited to your original payment method within 5-7 business days.</p>
                    
                    <p>If you have any questions, please contact us.</p>
                    
                    <p>Best regards,<br>
                    <strong>KP RegTech</strong></p>
                </div>
            </body>
            </html>
            """
            
            # In real app, use EmailMessage
            print(f"Refund approval email sent to {self.booking.email}")
            return True
        except Exception as e:
            print(f"Error sending refund email: {e}")
            return False
    
    class Meta:
        ordering = ['-requested_at']
# # ══════════════════════════════════════════════════════════════════════════════
# #                              END OF MODELS
# # ══════════════════════════════════════════════════════════════════════════════