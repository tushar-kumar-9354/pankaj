# admin.py - Complete fixed version
from django.contrib import admin
from .models import BlogPost, Testimonial, TestimonialSubmission
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_published', 'is_published', 'is_featured')
    list_filter = ('category', 'is_published', 'is_featured', 'date_published')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'date_published'
    list_editable = ('is_published', 'is_featured')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'is_published', 'is_featured')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'read_time')
        }),
        ('Media', {
            'fields': ('featured_image', 'image_url'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_published',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = (
        'client_name',
        'company',
        'industry',
        'rating',
        'is_featured',
        'is_active',
        'has_video',
    )
    
    list_filter = ('industry', 'is_featured', 'is_active')
    search_fields = ('client_name', 'company', 'content')
    list_editable = ('is_featured', 'is_active')  # Allow quick editing
    
    fieldsets = (
        ('Client Info', {
            'fields': ('client_name', 'company', 'position', 'industry')
        }),
        ('Testimonial Content', {
            'fields': ('content', 'rating', 'services')
        }),
        ('Media', {
            'fields': (
                'client_image',
                'image_url',
                'video_url',
                'video_thumbnail',
                'video',
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
    )
    
    def has_video(self, obj):
        return bool(obj.video or obj.video_url)
    has_video.boolean = True
    has_video.short_description = 'Has Video'

@admin.register(TestimonialSubmission)
class TestimonialSubmissionAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company_name', 'industry', 'status', 'submitted_date', 'has_profile_picture', 'has_testimonial']
    list_filter = ['status', 'industry', 'submitted_date']
    search_fields = ['full_name', 'company_name', 'email', 'testimonial_text']
    readonly_fields = ['submitted_date', 'approved_date', 'approved_testimonial']
    actions = ['approve_selected', 'reject_selected', 'create_missing_testimonials']
    
    fieldsets = (
        ('Client Information', {
            'fields': ('full_name', 'email', 'phone', 'company_name', 'position', 'industry')
        }),
        ('Testimonial Content', {
            'fields': ('testimonial_text', 'rating', 'services_used')
        }),
        ('Media', {
            'fields': ('profile_picture',),
            'classes': ('collapse',)
        }),
        ('Admin Status', {
            'fields': ('status', 'admin_notes', 'is_public', 'approved_testimonial'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('submitted_date', 'approved_date'),
            'classes': ('collapse',)
        }),
    )
    
    def has_profile_picture(self, obj):
        return bool(obj.profile_picture)
    has_profile_picture.boolean = True
    has_profile_picture.short_description = 'Has Photo'
    
    def has_testimonial(self, obj):
        return bool(obj.approved_testimonial)
    has_testimonial.boolean = True
    has_testimonial.short_description = 'Has Testimonial'
    
    def approve_selected(self, request, queryset):
        approved_count = 0
        for submission in queryset.filter(status='pending'):
            print(f"Processing approval for: {submission.full_name}")
            
            # Always create a new Testimonial object for approved submissions
            testimonial = Testimonial.objects.create(
                client_name=submission.full_name,
                company=submission.company_name,
                position=submission.position,
                content=submission.testimonial_text,
                industry=submission.industry,
                rating=submission.rating,
                services=submission.services_used,
                is_active=True,  # This makes it appear on website
                is_featured=False,  # Admin can mark as featured later
            )
            
            # Copy profile picture if exists
            if submission.profile_picture:
                print(f"Copying profile picture for {submission.full_name}")
                try:
                    testimonial.client_image.save(
                        submission.profile_picture.name,
                        submission.profile_picture.file,
                        save=True
                    )
                    print(f"Profile picture copied successfully")
                except Exception as e:
                    print(f"Error copying profile picture: {e}")
            
            # Update submission status and link to testimonial
            submission.status = 'approved'
            submission.approved_testimonial = testimonial
            submission.approved_date = timezone.now()
            submission.is_public = True
            submission.save()
            
            print(f"Created testimonial ID: {testimonial.id} for {testimonial.client_name}")
            approved_count += 1
            
            # Send approval email
            try:
                send_mail(
                    subject='Your Testimonial Has Been Published - Anjali Bansal & Associates',
                    message=f'''Dear {submission.full_name},
                    
Great news! Your testimonial has been approved and is now published on our website.

Thank you again for sharing your experience. We truly value your feedback.

View your testimonial here: https://yourwebsite.com/testimonials/

Best regards,
Anjali Bansal & Associates''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[submission.email],
                    fail_silently=True,
                )
                print(f"Approval email sent to {submission.email}")
            except Exception as e:
                print(f"Error sending email: {e}")
        
        self.message_user(request, f"{approved_count} testimonials approved and published.")
        print(f"Total approved: {approved_count}")
    
    def reject_selected(self, request, queryset):
        rejected_count = 0
        for submission in queryset.filter(status='pending'):
            submission.status = 'rejected'
            submission.save()
            
            # Send rejection email
            try:
                send_mail(
                    subject='Regarding Your Testimonial Submission - Anjali Bansal & Associates',
                    message=f'''Dear {submission.full_name},
                    
Thank you for submitting your testimonial. After careful review, we've decided not to publish it at this time.

We still appreciate your feedback and hope to serve you again in the future.

Best regards,
Anjali Bansal & Associates''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[submission.email],
                    fail_silently=True,
                )
            except:
                pass
            
            rejected_count += 1
        
        self.message_user(request, f"{rejected_count} testimonials rejected.")
    
    def create_missing_testimonials(self, request, queryset):
        """Create Testimonial objects for approved submissions that don't have them"""
        created_count = 0
        for submission in queryset.filter(status='approved', approved_testimonial__isnull=True):
            print(f"Creating missing testimonial for: {submission.full_name}")
            
            # Create new testimonial
            testimonial = Testimonial.objects.create(
                client_name=submission.full_name,
                company=submission.company_name,
                position=submission.position,
                content=submission.testimonial_text,
                industry=submission.industry,
                rating=submission.rating,
                services=submission.services_used,
                is_active=True,
                is_featured=False,
            )
            
            # Copy profile picture if exists
            if submission.profile_picture:
                try:
                    testimonial.client_image.save(
                        submission.profile_picture.name,
                        submission.profile_picture.file,
                        save=True
                    )
                except:
                    pass
            
            submission.approved_testimonial = testimonial
            submission.save()
            created_count += 1
        
        self.message_user(request, f"Created {created_count} missing testimonials from approved submissions.")
    
    def save_model(self, request, obj, form, change):
        # If status is being changed to approved manually via edit form
        if 'status' in form.changed_data and obj.status == 'approved':
            # Check if testimonial doesn't exist
            if not obj.approved_testimonial:
                # Create testimonial
                testimonial = Testimonial.objects.create(
                    client_name=obj.full_name,
                    company=obj.company_name,
                    position=obj.position,
                    content=obj.testimonial_text,
                    industry=obj.industry,
                    rating=obj.rating,
                    services=obj.services_used,
                    is_active=True,
                    is_featured=False,
                )
                
                # Copy profile picture
                if obj.profile_picture:
                    try:
                        testimonial.client_image.save(
                            obj.profile_picture.name,
                            obj.profile_picture.file,
                            save=True
                        )
                    except:
                        pass
                
                obj.approved_testimonial = testimonial
                obj.approved_date = timezone.now()
                obj.is_public = True
        
        super().save_model(request, obj, form, change)
    
    approve_selected.short_description = "Approve selected submissions"
    reject_selected.short_description = "Reject selected submissions"
    create_missing_testimonials.short_description = "Create Testimonial objects for approved submissions"