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

# Add to admin.py at the top
from .models import ConsultationBooking, AvailableSlot, BookedSlot

# Add these admin classes at the bottom
# In admin.py, update the ConsultationBookingAdmin class
# In admin.py, add/update the ConsultationBookingAdmin class

# In admin.py - Update ConsultationBookingAdmin class
 # In admin.py - Update ONLY the ConsultationBookingAdmin class
@admin.register(ConsultationBooking)
class ConsultationBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id_short', 'name', 'email', 'phone', 'appointment_date', 
                   'appointment_time', 'duration_display', 'mode_display', 'status', 
                   'is_paid', 'created_at', 'cancellable_badge', 'pending_at_display', 
                   'completed_at_display')
    
    list_filter = ('status', 'duration', 'mode', 'appointment_date', 'is_paid', 'created_at')
    search_fields = ('name', 'email', 'phone', 'company', 'booking_id', 'topic')
    readonly_fields = ('booking_id', 'created_at', 'updated_at', 'confirmed_at', 
                      'cancelled_at', 'pending_at', 'completed_at', 'booking_details', 
                      'cancellation_reason_display', 'is_cancellable_display')
    list_editable = ('status', 'is_paid')
    date_hierarchy = 'appointment_date'
    actions = ['mark_as_pending', 'mark_as_confirmed', 'mark_as_completed', 
               'cancel_selected_bookings', 'resend_confirmation_emails']
    
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
            'fields': ('cancellation_reason', 'cancellation_reason_display'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'is_cancellable_display'),
            'classes': ('collapse',)
        }),
    )
    
    # Methods must be defined INSIDE the class with proper indentation
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
    
    def pending_at_display(self, obj):
        if obj.pending_at:
            return obj.pending_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    pending_at_display.short_description = 'Pending At'
    
    def completed_at_display(self, obj):
        if obj.completed_at:
            return obj.completed_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    completed_at_display.short_description = 'Completed At'
    
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
    
    # Admin actions
    def mark_as_pending(self, request, queryset):
        """Mark selected bookings as pending"""
        from django.utils import timezone
        from .views import send_status_change_email
        
        updated_count = 0
        emails_sent = 0
        
        for booking in queryset:
            old_status = booking.status
            booking.status = 'pending'
            booking.pending_at = timezone.now()
            booking.save()
            
            # Send status change email
            try:
                send_status_change_email(booking, 'pending', old_status)
                emails_sent += 1
            except Exception as e:
                self.message_user(request, f"Error sending email for booking {booking.booking_id}: {str(e)}", level='ERROR')
            
            updated_count += 1
        
        self.message_user(request, 
            f"Marked {updated_count} booking(s) as pending. {emails_sent} notification email(s) sent.")
    mark_as_pending.short_description = "Mark as pending"
    
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
    
    def resend_confirmation_emails(self, request, queryset):
        """Resend confirmation emails for selected bookings"""
        from .views import send_booking_confirmation_email
        
        sent_count = 0
        for booking in queryset.exclude(status='cancelled'):
            try:
                details = {
                    'title': f"{booking.get_duration_display()} Consultation",
                    'price_amount': float(booking.price)
                }
                
                if send_booking_confirmation_email(booking, details):
                    sent_count += 1
            except Exception as e:
                self.message_user(request, f"Error sending email for {booking.booking_id}: {str(e)}", level='ERROR')
        
        self.message_user(request, f"Confirmation emails sent to {sent_count} client(s).")
    resend_confirmation_emails.short_description = "📧 Resend confirmation emails"
    
    # Save model method - FIXED VERSION
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
                
                # ALWAYS send email when status changes, regardless of previous status
                if new_status != old_status:
                    # Send status change email (this will send for ALL status changes)
                    try:
                        email_sent = send_status_change_email(obj, new_status, old_status)
                        if email_sent:
                            self.message_user(request, 
                                f"Status changed from '{old_status}' to '{new_status}'. Notification email sent to {obj.email}.")
                        else:
                            self.message_user(request, 
                                f"Status changed from '{old_status}' to '{new_status}'. Failed to send email.", 
                                level='WARNING')
                    except Exception as e:
                        self.message_user(request, 
                            f"Error sending status change email: {str(e)}", 
                            level='ERROR')
                return  # Don't continue further
                    
            except ConsultationBooking.DoesNotExist:
                pass  # New object
        
        # For new objects or if status didn't change
        super().save_model(request, obj, form, change)
        
        # For new bookings, send confirmation email
        if not change and obj.status == 'confirmed':
            try:
                from .views import send_booking_confirmation_email
                details = {
                    'title': f"{obj.get_duration_display()} Consultation",
                    'price_amount': float(obj.price)
                }
                send_booking_confirmation_email(obj, details)
                self.message_user(request, f"Confirmation email sent to {obj.email}")
            except Exception as e:
                self.message_user(request, f"Error sending confirmation email: {str(e)}", level='ERROR')
    
    # Change form template
    change_form_template = 'admin/consultationbooking_change_form.html'
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
        
        # ALWAYS send notification for status change
        try:
            send_status_change_email(booking, 'confirmed', old_status)
            emails_sent += 1
        except Exception as e:
            self.message_user(request, f"Error sending email for booking {booking.booking_id}: {str(e)}", level='ERROR')
        
        updated_count += 1
    
    self.message_user(request, 
        f"Marked {updated_count} booking(s) as confirmed. {emails_sent} notification email(s) sent.")

# Similarly update other actions (mark_as_pending, mark_as_completed, cancel_selected_bookings)
# to use send_status_change_email instead of specific email functions
    mark_as_confirmed.short_description = "Mark as confirmed"
    
    def mark_as_completed(self, request, queryset):
        """Mark selected bookings as completed"""
        from django.utils import timezone
        from .views import send_status_change_email
        
        updated_count = 0
        emails_sent = 0
        
        for booking in queryset.exclude(status='cancelled'):
            original_status = booking.status
            booking.status = 'completed'
            booking.completed_at = timezone.now()
            booking.save()
            
            # Send completion notification
            try:
                send_status_change_email(booking, 'completed', original_status)
                emails_sent += 1
            except Exception as e:
                self.message_user(request, f"Error sending email for booking {booking.booking_id}: {str(e)}", level='ERROR')
            
            updated_count += 1
        
        self.message_user(request, f"Marked {updated_count} booking(s) as completed. {emails_sent} notification email(s) sent.")
    
    mark_as_completed.short_description = "Mark as completed"
    
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
    cancellation_reason_display.short_description = 'Cancellation Reason Display'
    
    def cancel_bookings_action(self, request, queryset):
        """Cancel selected bookings"""
        from .views import send_cancellation_email
        from django.utils import timezone
        
        cancelled_count = 0
        for booking in queryset.exclude(status='cancelled'):
            # Ask for cancellation reason
            reason = f"Booking cancelled by admin on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Update booking
            booking.status = 'cancelled'
            booking.cancellation_reason = reason
            booking.cancelled_at = timezone.now()
            booking.save()
            
            # Send email
            try:
                send_cancellation_email(booking, reason)
            except Exception as e:
                self.message_user(request, f"Error sending email for {booking.booking_id}: {str(e)}", level='ERROR')
            
            cancelled_count += 1
        
        if cancelled_count == 1:
            message = "1 booking was cancelled"
        else:
            message = f"{cancelled_count} bookings were cancelled"
        
        self.message_user(request, f"{message}. Cancellation emails were sent to clients.")
    
    cancel_bookings_action.short_description = "🚫 Cancel selected bookings"
    
    def resend_confirmation_emails(self, request, queryset):
        """Resend confirmation emails"""
        from .views import send_booking_confirmation_email
        
        sent_count = 0
        for booking in queryset.exclude(status='cancelled'):
            try:
                details = {
                    'title': f"{booking.get_duration_display()} Consultation",
                    'price_amount': float(booking.price)
                }
                
                if send_booking_confirmation_email(booking, details):
                    sent_count += 1
            except Exception as e:
                self.message_user(request, f"Error sending email for {booking.booking_id}: {str(e)}", level='ERROR')
        
        self.message_user(request, f"Confirmation emails sent to {sent_count} client(s).")
    
    resend_confirmation_emails.short_description = "📧 Resend confirmation emails"
    
    # Add change form template to show cancellation warning
    change_form_template = 'admin/consultationbooking_change_form.html'
    list_display = ('booking_id_short', 'name', 'email', 'phone', 'appointment_date', 
                   'appointment_time', 'duration_display', 'mode_display', 'status', 
                   'is_paid', 'created_at', 'is_cancellable')
    list_filter = ('status', 'duration', 'mode', 'appointment_date', 'is_paid', 'created_at')
    search_fields = ('name', 'email', 'phone', 'company', 'booking_id', 'topic')
    readonly_fields = ('booking_id', 'created_at', 'updated_at', 'confirmed_at', 
                      'cancelled_at', 'booking_details', 'is_cancellable_display')
    list_editable = ('status', 'is_paid')
    date_hierarchy = 'appointment_date'
    actions = ['cancel_selected_bookings', 'send_confirmation_emails', 'mark_as_completed']
    
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
        ('Cancellation Details', {
            'fields': ('cancellation_reason', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'is_cancellable_display'),
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
    
    def is_cancellable(self, obj):
        return obj.is_cancellable()
    is_cancellable.boolean = True
    is_cancellable.short_description = 'Cancellable'
    
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
    
    # ADD THIS METHOD TO HANDLE CANCELLATION
    def cancel_selected_bookings(self, request, queryset):
        """Admin action to cancel selected bookings"""
        cancelled_count = 0
        emails_sent = 0
        
        for booking in queryset.exclude(status='cancelled'):
            # Update booking status
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.save()
            
            # Send cancellation email
            try:
                from .views import send_cancellation_email
                email_sent = send_cancellation_email(booking)
                if email_sent:
                    emails_sent += 1
            except Exception as e:
                self.message_user(request, f"Error sending email for booking {booking.booking_id}: {str(e)}", level='ERROR')
            
            cancelled_count += 1
        
        self.message_user(request, f"Successfully cancelled {cancelled_count} booking(s). {emails_sent} cancellation email(s) sent.")
    
    cancel_selected_bookings.short_description = "Cancel selected bookings"
    
    # ADD THIS METHOD TO SEND CONFIRMATION EMAILS
    def send_confirmation_emails(self, request, queryset):
        """Resend confirmation emails for selected bookings"""
        emails_sent = 0
        
        for booking in queryset.exclude(status='cancelled'):
            try:
                from .views import send_booking_confirmation_email
                
                # Create details dictionary
                details = {
                    'title': f"{booking.get_duration_display()} Consultation",
                    'price_amount': float(booking.price)
                }
                
                email_sent = send_booking_confirmation_email(booking, details)
                if email_sent:
                    emails_sent += 1
            except Exception as e:
                self.message_user(request, f"Error sending email for booking {booking.booking_id}: {str(e)}", level='ERROR')
        
        self.message_user(request, f"Successfully sent {emails_sent} confirmation email(s).")
    
    send_confirmation_emails.short_description = "Resend confirmation emails"
    
    # ADD THIS METHOD TO MARK AS COMPLETED
    def mark_as_completed(self, request, queryset):
        """Mark selected bookings as completed"""
        completed_count = 0
        
        for booking in queryset.exclude(status='cancelled'):
            booking.status = 'completed'
            booking.save()
            completed_count += 1
        
        self.message_user(request, f"Successfully marked {completed_count} booking(s) as completed.")
    
    mark_as_completed.short_description = "Mark as completed"
    
    # ADD THIS TO OVERRIDE SAVE MODEL
    def save_model(self, request, obj, form, change):
        # Check if status is being changed to cancelled
        if 'status' in form.changed_data and obj.status == 'cancelled' and not obj.cancelled_at:
            obj.cancelled_at = timezone.now()
            
            # Send cancellation email
            try:
                from .views import send_cancellation_email
                send_cancellation_email(obj)
                self.message_user(request, f"Cancellation email sent to {obj.email}")
            except Exception as e:
                self.message_user(request, f"Error sending cancellation email: {str(e)}", level='ERROR')
        
        super().save_model(request, obj, form, change)
    list_display = ('booking_id_short', 'name', 'email', 'phone', 'appointment_date', 
                   'appointment_time', 'duration_display', 'mode_display', 'status', 
                   'is_paid', 'created_at')
    list_filter = ('status', 'duration', 'mode', 'appointment_date', 'is_paid', 'created_at')
    search_fields = ('name', 'email', 'phone', 'company', 'booking_id', 'topic')
    readonly_fields = ('booking_id', 'created_at', 'updated_at', 'confirmed_at', 'booking_details')
    list_editable = ('status', 'is_paid')
    date_hierarchy = 'appointment_date'
    
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
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'confirmed_at'),
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
@admin.register(AvailableSlot)
class AvailableSlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'max_bookings', 'is_active')
    list_filter = ('day', 'is_active')
    list_editable = ('max_bookings', 'is_active')
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('day', 'start_time')

@admin.register(BookedSlot)
class BookedSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'slot', 'booking')
    list_filter = ('date', 'slot__day')
    search_fields = ('booking__name', 'booking__email')
    readonly_fields = ('date', 'slot', 'booking')
    
    def has_add_permission(self, request):
        return False  # BookedSlots should only be created via booking process