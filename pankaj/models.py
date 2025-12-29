
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