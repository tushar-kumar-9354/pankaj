# admin.py - Fixed version with proper indentation
from traceback import format_tb
from django.contrib import admin
from flask import redirect
from .models import BlogPost, Testimonial, TestimonialSubmission, ConsultationBooking, AvailableSlot
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_published', 'is_published', 'is_featured', 'read_count')
    list_filter = ('category', 'is_published', 'is_featured', 'date_published')
    search_fields = ('title', 'content', 'excerpt')
    date_hierarchy = 'date_published'
    list_editable = ('is_published', 'is_featured')
    readonly_fields = ('date_created', 'date_modified', 'read_count', 'slug')  # Add slug to readonly
    actions = ['publish_selected', 'unpublish_selected', 'feature_selected', 'unfeature_selected']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'is_published', 'is_featured', 'read_count')  # Keep slug here but it will be readonly
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'read_time'),
            'description': 'Write your blog content here. Use the formatting toolbar for rich text.'
        }),
        ('Media', {
            'fields': ('featured_image', 'image_url'),
            'classes': ('collapse',),
            'description': 'Upload a featured image (recommended size: 1200x630px)'
        }),
        ('SEO & Meta', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
            'description': 'Optimize your blog post for search engines'
        }),
        ('Publishing', {
            'fields': ('date_published', 'author', 'date_created', 'date_modified'),
            'classes': ('collapse',),
            'description': 'Schedule publication date or publish immediately'
        }),
    )
    
    # Remove the prepopulated_fields since slug is auto-generated
    # prepopulated_fields = {'slug': ('title',)}  # REMOVE THIS LINE
    
    class Media:
        css = {
            'all': ('css/admin-blog.css',)
        }
        js = ('js/admin-blog.js',)
    
    def get_queryset(self, request):
        # Only show blogs created by current admin (if not superuser)
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
    
    def save_model(self, request, obj, form, change):
        # Automatically set author to current user if not set
        if not obj.author:
            obj.author = request.user
        
        # If publishing now but no date set, use current time
        if obj.is_published and not obj.date_published:
            obj.date_published = timezone.now()
        
        # If date published is in future, don't publish yet
        if obj.date_published and obj.date_published > timezone.now():
            obj.is_published = False
        
        # Force save to ensure slug gets generated
        super().save_model(request, obj, form, change)
        
        # Check if slug was generated
        if not obj.slug or str(obj.slug).strip() == '':
            # Regenerate and save again
            from django.utils.text import slugify
            import uuid
            
            if obj.title and obj.title.strip() != '':
                base_slug = slugify(obj.title)
            else:
                base_slug = f"blog-{uuid.uuid4().hex[:8]}"
            
            if not base_slug or base_slug.strip() == '':
                base_slug = f"blog-post-{uuid.uuid4().hex[:8]}"
            
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exclude(id=obj.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            obj.slug = slug
            obj.save(update_fields=['slug'])
    
    def publish_selected(self, request, queryset):
        """Publish selected blog posts."""
        updated = queryset.update(
            is_published=True,
            date_published=timezone.now()
        )
        self.message_user(request, f"{updated} blog posts published successfully.")
    
    def unpublish_selected(self, request, queryset):
        """Unpublish selected blog posts."""
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} blog posts unpublished.")
    
    def feature_selected(self, request, queryset):
        """Mark selected blog posts as featured."""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} blog posts marked as featured.")
    
    def unfeature_selected(self, request, queryset):
        """Remove featured status from selected blog posts."""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} blog posts removed from featured.")
    
    publish_selected.short_description = "Publish selected posts"
    unpublish_selected.short_description = "Unpublish selected posts"
    feature_selected.short_description = "Mark as featured"
    unfeature_selected.short_description = "Remove featured status"
    
    # Add a method to track reads
    def read_count(self, obj):
        return getattr(obj, 'view_count', 0)
    read_count.short_description = 'Views'

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = (
        'client_name',
        'company',
        'industry',
        'rating',
        'is_featured',
        'is_active',
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
                
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
    )
    
    
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
                    subject='Your Testimonial Has Been Published - KP RegTech',
                    message=f'''Dear {submission.full_name},
                    
Great news! Your testimonial has been approved and is now published on our website.

Thank you again for sharing your experience. We truly value your feedback.

View your testimonial here: https://yourwebsite.com/testimonials/

Best regards,
KP RegTech''',
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
                    subject='Regarding Your Testimonial Submission - KP RegTech',
                    message=f'''Dear {submission.full_name},
                    
Thank you for submitting your testimonial. After careful review, we've decided not to publish it at this time.

We still appreciate your feedback and hope to serve you again in the future.

Best regards,
KP RegTech''',
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

@admin.register(ConsultationBooking)
class ConsultationBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id_short', 'name', 'email', 'phone', 'appointment_date', 
                   'appointment_time', 'duration_display', 'mode_display', 'status', 
                   'is_paid', 'created_at', 'cancellable_badge')
    
    list_filter = ('status', 'duration', 'mode', 'appointment_date', 'is_paid', 'created_at')
    search_fields = ('name', 'email', 'phone', 'company', 'booking_id', 'topic')
    readonly_fields = ('booking_id', 'created_at', 'updated_at', 'confirmed_at', 
                      'cancelled_at', 'pending_at', 'completed_at', 'booking_details', 
                      'cancellation_reason_display', 'is_cancellable_display')
    list_editable = ('status', 'is_paid')
    date_hierarchy = 'appointment_date'
    actions = ['mark_as_confirmed', 'mark_as_completed', 'cancel_selected_bookings', 'download_selected_bookings']
    def download_selected_bookings(self, request, queryset):
        """Generate PDF for selected bookings."""
        if queryset.count() == 1:
            booking = queryset.first()
            from django.urls import reverse
            url = reverse('download_booking_details', kwargs={'booking_id': booking.booking_id})
            return redirect(f"{url}?format=pdf")
        else:
            self.message_user(request, "Please select only one booking to download.", level='WARNING')
    
    download_selected_bookings.short_description = "Download booking details (PDF)"
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'duration', 'price', 'status', 'is_paid', 'payment_id')
        }),
        ('Appointment Details', {
            'fields': ('appointment_date', 'appointment_time', 'mode')
        }),
        ('Client Information', {
            'fields': ('name', 'email', 'phone', 'company', 'designation')
        }),
        ('Consultation Details', {
            'fields': ('topic', 'documents', 'additional_notes', 'newsletter_consent')
        }),
        ('Status Timestamps', {
            'fields': ('pending_at', 'confirmed_at', 'completed_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('Cancellation Details', {
            'fields': ('cancellation_reason',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def booking_id_short(self, obj):
        return str(obj.booking_id)[:8] + "..."
    booking_id_short.short_description = 'Booking ID'
    
    def duration_display(self, obj):
        return obj.get_duration_display()
    duration_display.short_description = 'Duration'
    
    def mode_display(self, obj):
        return obj.get_mode_display()
    mode_display.short_description = 'Mode'
    
    def cancellable_badge(self, obj):
        if obj.status == 'cancelled':
            return '❌ Cancelled'
        elif obj.is_cancellable():
            return '✅ Cancellable'
        else:
            return '⏳ Within 24h'
    cancellable_badge.short_description = 'Cancellation'
    
    def cancellation_reason_display(self, obj):
        if obj.cancellation_reason:
            return f"❌ {obj.cancellation_reason}"
        return "No reason provided"
    cancellation_reason_display.short_description = 'Cancellation Reason'
    
    def is_cancellable_display(self, obj):
        return f"{'Yes' if obj.is_cancellable() else 'No'} - {'Can be cancelled' if obj.is_cancellable() else 'Cannot be cancelled (within 24 hours or already cancelled)'}"
    is_cancellable_display.short_description = 'Cancellation Status'
    
    def booking_details(self, obj):
        return f"""
        <div style="background: #f9f9f9; padding: 10px; border-radius: 5px;">
            <strong>Client:</strong> {obj.name}<br>
            <strong>Email:</strong> {obj.email}<br>
            <strong>Phone:</strong> {obj.phone}<br>
            <strong>Company:</strong> {obj.company or 'N/A'}<br>
            <strong>Topic:</strong> {obj.topic[:100]}...
        </div>
        """
    booking_details.short_description = 'Booking Details'
    booking_details.allow_tags = True
    
    def mark_as_confirmed(self, request, queryset):
        """Mark selected bookings as confirmed"""
        from django.utils import timezone
        from .views import send_status_change_email
        
        updated_count = 0
        emails_sent = 0
        
        for booking in queryset:
            old_status = booking.status
            booking.status = 'confirmed'
            booking.confirmed_at = timezone.now()
            booking.save()
            
            # Send status change email
            try:
                send_status_change_email(booking, 'confirmed', old_status)
                emails_sent += 1
            except Exception as e:
                self.message_user(request, f"Error sending email for booking {booking.booking_id}: {str(e)}", level='ERROR')
            
            updated_count += 1
        
        self.message_user(request, 
            f"Marked {updated_count} booking(s) as confirmed. {emails_sent} notification email(s) sent.")
    mark_as_confirmed.short_description = "Mark as confirmed"
    
    def mark_as_completed(self, request, queryset):
        """Mark selected bookings as completed"""
        from django.utils import timezone
        from .views import send_status_change_email
        
        updated_count = 0
        emails_sent = 0
        
        for booking in queryset:
            old_status = booking.status
            booking.status = 'completed'
            booking.completed_at = timezone.now()
            booking.save()
            
            # Send status change email
            try:
                send_status_change_email(booking, 'completed', old_status)
                emails_sent += 1
            except Exception as e:
                self.message_user(request, f"Error sending email for booking {booking.booking_id}: {str(e)}", level='ERROR')
            
            updated_count += 1
        
        self.message_user(request, 
            f"Marked {updated_count} booking(s) as completed. {emails_sent} notification email(s) sent.")
    mark_as_completed.short_description = "Mark as completed"
    
    def cancel_selected_bookings(self, request, queryset):
        """Admin action to cancel selected bookings"""
        from django.utils import timezone
        from .views import send_status_change_email
        
        cancelled_count = 0
        emails_sent = 0
        
        for booking in queryset:
            old_status = booking.status
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.save()
            
            # Send status change email
            try:
                send_status_change_email(booking, 'cancelled', old_status)
                emails_sent += 1
            except Exception as e:
                self.message_user(request, f"Error sending email for booking {booking.booking_id}: {str(e)}", level='ERROR')
            
            cancelled_count += 1
        
        self.message_user(request, 
            f"Successfully cancelled {cancelled_count} booking(s). {emails_sent} notification email(s) sent.")
    cancel_selected_bookings.short_description = "Cancel selected bookings"
    
    def save_model(self, request, obj, form, change):
        if change:  # Existing object being changed
            from django.utils import timezone
            from .views import send_status_change_email
            
            # Get original object from database
            try:
                original = ConsultationBooking.objects.get(pk=obj.pk)
                old_status = original.status
                new_status = obj.status
                
                # Update timestamps based on new status
                if new_status == 'pending' and not obj.pending_at:
                    obj.pending_at = timezone.now()
                elif new_status == 'confirmed' and not obj.confirmed_at:
                    obj.confirmed_at = timezone.now()
                elif new_status == 'completed' and not obj.completed_at:
                    obj.completed_at = timezone.now()
                elif new_status == 'cancelled' and not obj.cancelled_at:
                    obj.cancelled_at = timezone.now()
                
                # Save the object first to ensure timestamps are updated
                super().save_model(request, obj, form, change)
                
                # Send email when status changes
                if new_status != old_status:
                    try:
                        email_sent = send_status_change_email(obj, new_status, old_status)
                        if email_sent:
                            self.message_user(request, 
                                f"Status changed from '{old_status}' to '{new_status}'. Notification email sent to {obj.email}.")
                    except Exception as e:
                        self.message_user(request, 
                            f"Error sending status change email: {str(e)}", 
                            level='ERROR')
                return
                    
            except ConsultationBooking.DoesNotExist:
                pass
        
        # For new objects or if status didn't change
        super().save_model(request, obj, form, change)

@admin.register(AvailableSlot)
class AvailableSlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'max_bookings', 'is_active')
    list_filter = ('day', 'is_active')
    list_editable = ('max_bookings', 'is_active')
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('day', 'start_time')

# from .models import Payment

# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('payment_id', 'booking', 'amount', 'method', 'status', 'created_at')
#     list_filter = ('status', 'method', 'created_at')
#     search_fields = ('payment_id', 'booking__booking_id', 'booking__name', 'booking__email')
#     readonly_fields = ('created_at', 'updated_at', 'completed_at')
#     list_editable = ('status',)
    
#     fieldsets = (
#         ('Payment Information', {
#             'fields': ('booking', 'payment_id', 'razorpay_order_id', 'razorpay_payment_id')
#         }),
#         ('Payment Details', {
#             'fields': ('amount', 'currency', 'method', 'status')
#         }),
#         ('Payment Method Details', {
#             'fields': ('upi_id', 'card_last4', 'bank_name'),
#             'classes': ('collapse',)
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at', 'completed_at'),
#             'classes': ('collapse',)
#         }),
#         ('Error Information', {
#             'fields': ('error_code', 'error_description'),
#             'classes': ('collapse',)
#         }),
#     )

from django.utils.html import format_html
from .models import Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'booking_link', 'amount', 'method', 'status_display', 'is_paid_display', 'created_at')
    list_filter = ('status', 'method', 'created_at', 'cash_payment_verified')
    search_fields = ('payment_id', 'booking__booking_id', 'booking__name')
    readonly_fields = ('payment_id', 'created_at', 'completed_at', 'cash_payment_verified_at')
    
    def booking_link(self, obj):
        if obj.booking:
            return format_html('<a href="/admin/consultation/consultationbooking/{}/change/">{}</a>', 
                              obj.booking.id, obj.booking.booking_id)
        return "No Booking"
    booking_link.short_description = 'Booking'
    
    def status_display(self, obj):
        if obj.method == 'cash' and not obj.cash_payment_verified:
            return format_html('<span style="color: orange;">⏳ Pending Verification</span>')
        elif obj.status == 'success':
            return format_html('<span style="color: green;">✅ Paid</span>')
        elif obj.status == 'pending':
            return format_html('<span style="color: orange;">⏳ Pending</span>')
        else:
            return format_html('<span style="color: red;">❌ {}</span>', obj.get_status_display())
    status_display.short_description = 'Status'
    
    def is_paid_display(self, obj):
        if not obj.booking:
            return format_html('<span style="color: red;">❌ No Booking</span>')
        if obj.method == 'cash' and not obj.cash_payment_verified:
            return format_html('<span style="color: orange;">⏳ Pending</span>')
        return format_html('<span style="color: green;">✅</span>' if obj.booking.is_paid else '<span style="color: red;">❌</span>')
    is_paid_display.short_description = 'Paid'
    
    def get_queryset(self, request):
        """Optimize query to select related booking"""
        return super().get_queryset(request).select_related('booking')
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'booking', 'amount', 'method', 'status', 'transaction_id')
        }),
        ('Cash Payment Verification', {
            'fields': ('cash_payment_verified', 'cash_payment_verified_by', 'cash_payment_verified_at', 'cash_payment_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

from .models import BlogSubscriber

@admin.register(BlogSubscriber)
class BlogSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'is_verified', 'subscribed_at')
    list_filter = ('is_active', 'is_verified', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at', 'unsubscribed_at', 'verification_token')
    actions = ['activate_subscribers', 'deactivate_subscribers', 
               'send_verification_emails', 'test_email_send']
    
    def test_email_send(self, request, queryset):
        """Test sending verification emails."""
        for subscriber in queryset:
            success = subscriber.send_verification_email()
            if success:
                self.message_user(request, f"Test email sent to {subscriber.email}")
            else:
                self.message_user(request, f"Failed to send email to {subscriber.email}", level='ERROR')
    
    test_email_send.short_description = "Send test verification email"
    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscribers activated.')
    
    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f'{updated} subscribers deactivated.')
    
    def send_verification_emails(self, request, queryset):
        sent_count = 0
        for subscriber in queryset.filter(is_verified=False):
            if subscriber.send_verification_email():
                sent_count += 1
        self.message_user(request, f'Verification emails sent to {sent_count} subscribers.')
    
    activate_subscribers.short_description = "Activate selected subscribers"
    deactivate_subscribers.short_description = "Deactivate selected subscribers"
    send_verification_emails.short_description = "Send verification emails"