# ══════════════════════════════════════════════════════════════════════════════
#                                   IMPORTS
# ══════════════════════════════════════════════════════════════════════════════

# Django Core Imports
from django.shortcuts import render, get_object_or_404, redirect  # Rendering, data retrieval, redirection
from django.core.paginator import Paginator  # For paginating query results
from django.contrib import messages  # For user feedback messages
from django.contrib.admin.views.decorators import staff_member_required  # Restrict views to staff
from django.conf import settings  # Access Django settings
from django.core.mail import send_mail, EmailMessage  # Email sending functionality
from django.utils import timezone  # Timezone-aware datetime handling
from django.http import HttpResponse, JsonResponse  # HTTP response types
from django.db.models.functions import Lower, Trim  # Database function utilities
from django.db.models import Avg, Count  # Database aggregation functions
from django.template.loader import render_to_string  # Template rendering to string

# Standard Library Imports
from datetime import datetime, timedelta, date, time  # Date/time manipulation
import logging  # Application logging

# Application-Specific Imports
from .models import BlogPost, Testimonial, TestimonialSubmission, ConsultationBooking, AvailableSlot, BookedSlot
from .forms import TestimonialSubmissionForm  # Form for testimonial submissions

# ─── Logger Setup ──────────────────────────────────────────────────────────────
# Initialize logger for this module
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
#                              CORE WEBSITE VIEWS
# ══════════════════════════════════════════════════════════════════════════════

def index(request):
    """
    Homepage view - displays latest blog posts and featured testimonials.
    
    Returns:
        Rendered homepage template with context data
    """
    # Get latest 3 published blog posts for homepage display
    latest_blogs = BlogPost.objects.filter(is_published=True)[:3]
    
    # Get active featured testimonials for homepage carousel/slider
    testimonials = Testimonial.objects.filter(is_active=True, is_featured=True)[:4]
    
    # Prepare context dictionary for template
    context = {
        'latest_blogs': latest_blogs,
        'testimonials': testimonials,
    }
    
    # Render homepage template with context
    return render(request, "index.html", context)


def about(request):
    """About page view."""
    return render(request, "about.html")


def our_expertise(request):
    """Our Expertise page view."""
    return render(request, "our_expertise.html")


def contact(request):
    """Contact page view."""
    return render(request, "contact.html")


def services(request):
    """Services page view."""
    return render(request, 'services.html')


# ══════════════════════════════════════════════════════════════════════════════
#                               BLOG VIEWS
# ══════════════════════════════════════════════════════════════════════════════

def blogs(request):
    """
    Main blog listing page with filtering, sorting, and pagination.
    
    Features:
        - Category filtering
        - Sorting options (latest, oldest, popular)
        - Pagination (3 posts per page)
        - Distinct category list for filters
    """
    # Start with all published blog posts
    all_blogs = BlogPost.objects.filter(is_published=True)
    
    # ─── Category Filtering ────────────────────────────────────────────────────
    # Get category from query parameters (e.g., ?category=FEMA)
    category_filter = request.GET.get('category')
    
    # Apply category filter if specified (exact match)
    if category_filter:
        all_blogs = all_blogs.filter(category=category_filter)
    
    # ─── Get Distinct Categories ───────────────────────────────────────────────
    # Retrieve all unique categories from published posts for filter dropdown
    categories = (
        BlogPost.objects
        .filter(is_published=True)
        .values_list('category', flat=True)  # Get only category values
        .distinct()  # Ensure uniqueness
        .order_by('category')  # Alphabetical order
    )
    
    # ─── Sorting ───────────────────────────────────────────────────────────────
    # Get sort parameter from query string, default to 'latest'
    sort_by = request.GET.get('sort', 'latest')
    
    # Apply sorting based on user selection
    if sort_by == 'oldest':
        all_blogs = all_blogs.order_by('date_published')  # Oldest first
    elif sort_by == 'popular':
        all_blogs = all_blogs.order_by('-read_time')  # Highest read time first
    else:  # Default to 'latest'
        all_blogs = all_blogs.order_by('-date_published')  # Most recent first
    
    # ─── Pagination ────────────────────────────────────────────────────────────
    # Split results into pages (3 posts per page)
    paginator = Paginator(all_blogs, 3)
    
    # Get current page number from query parameters
    page_number = request.GET.get('page')
    
    # Get page object for current page
    page_obj = paginator.get_page(page_number)
    
    # ─── Prepare Context ───────────────────────────────────────────────────────
    return render(request, "blogs.html", {
        'blogs': page_obj,  # Current page's blog posts
        'categories': categories,  # All available categories
        'current_category': category_filter,  # Currently selected category
        'current_sort': sort_by,  # Currently selected sort option
        'page_obj': page_obj,  # Page object for template pagination controls
    })


def blog_detail(request, slug):
    """
    Individual blog post detail view.
    
    Args:
        slug: URL-friendly identifier for the blog post
    
    Returns:
        Rendered blog detail template with post and related posts
    """
    # Get the specific blog post by slug, ensure it's published
    blog = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Get related posts from the same category (excluding current post)
    related_posts = BlogPost.objects.filter(
        category=blog.category, 
        is_published=True
    ).exclude(id=blog.id)[:3]  # Limit to 3 related posts
    
    # Prepare context for template
    context = {
        'blog': blog,  # Main blog post
        'related_posts': related_posts,  # Related posts for sidebar/related section
    }
    
    # Render blog detail template
    return render(request, "blog_detail.html", context)


# ══════════════════════════════════════════════════════════════════════════════
#                              TESTIMONIAL VIEWS
# ══════════════════════════════════════════════════════════════════════════════

def testimonials(request):
    """
    Main testimonials page with industry filtering and statistics.
    
    Features:
        - Industry-based tabbed organization
        - Featured testimonials slider
        - Video testimonials section
        - Statistics dashboard
        - Admin notification for pending submissions
    """
    # ─── Get Testimonials Data ────────────────────────────────────────────────
    # All active testimonials
    all_testimonials = Testimonial.objects.filter(is_active=True)
    
    # Featured testimonials for the main slider
    featured_testimonials = Testimonial.objects.filter(
        is_active=True, 
        is_featured=True
    )
    
    # ─── Industry Data Organization ───────────────────────────────────────────
    # Get unique industries from active testimonials for tab headers
    industries = Testimonial.objects.filter(is_active=True).values_list(
        'industry', flat=True
    ).distinct()
    
    # Group testimonials by industry for tabbed display
    testimonials_by_industry = {}
    for testimonial in all_testimonials:
        industry = testimonial.industry
        if industry not in testimonials_by_industry:
            testimonials_by_industry[industry] = []
        testimonials_by_industry[industry].append(testimonial)
    
    # Create QuerySet for each industry for easier template access
    industry_testimonials = {}
    for industry in industries:
        industry_testimonials[industry] = Testimonial.objects.filter(
            industry=industry, 
            is_active=True
        )
    
    # ─── Statistics ───────────────────────────────────────────────────────────
    # Calculate key metrics for display
    stats = {
        'total_clients': Testimonial.objects.filter(is_active=True).count(),
        'avg_rating': round(Testimonial.objects.filter(is_active=True).aggregate(
            Avg('rating')
        )['rating__avg'] or 0, 1),  # Default to 0 if no ratings
        'industries_served': len(industries),  # Count of unique industries
    }
    
    # ─── Video Testimonials ───────────────────────────────────────────────────
    # Get testimonials with video URLs
    video_testimonials = Testimonial.objects.filter(
        is_active=True,
        video_url__isnull=False  # Has a video URL
    ).exclude(video_url="")  # Exclude empty URLs
    
    # ─── Admin Features ───────────────────────────────────────────────────────
    # Show pending submissions count to admin users
    pending_submissions = None
    if request.user.is_staff:
        pending_submissions = TestimonialSubmission.objects.filter(
            status='pending'
        ).count()
    
    # ─── Prepare Context ───────────────────────────────────────────────────────
    context = {
        'all_testimonials': all_testimonials,  # All active testimonials
        'featured_testimonials': featured_testimonials,  # Featured slider items
        'testimonials_by_industry': testimonials_by_industry,  # Dictionary by industry
        'industry_testimonials': industry_testimonials,  # QuerySet per industry
        'industries': industries,  # Unique industry list
        'stats': stats,  # Statistics dictionary
        'video_testimonials': video_testimonials,  # Video testimonials
        'pending_submissions': pending_submissions,  # Admin-only data
    }
    
    # Render testimonials template
    return render(request, "testimonials.html", context)


def submit_testimonial(request):
    """
    View for users to submit new testimonials.
    
    Handles:
        - Form display (GET)
        - Form submission (POST)
        - Email notifications (user confirmation, admin alert)
    """
    if request.method == 'POST':
        # Process form submission
        form = TestimonialSubmissionForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Save form data but don't commit to database yet
            submission = form.save(commit=False)
            submission.status = 'pending'  # Set initial status
            submission.save()  # Now save to database
            
            # ─── User Confirmation Email ───────────────────────────────────────
            try:
                send_mail(
                    subject='Testimonial Submission Received - Anjali Bansal & Associates',
                    message=f'''Dear {submission.full_name},
                    
Thank you for submitting your testimonial! We truly appreciate you taking the time to share your experience.

Your submission is now under review. We'll notify you once it's approved and published on our website.

If you have any questions, please don't hesitate to contact us.

Best regards,
Anjali Bansal & Associates''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[submission.email],
                    fail_silently=True,  # Don't crash if email fails
                )
            except:
                pass  # Email failure shouldn't break submission
            
            # ─── Admin Notification Email ──────────────────────────────────────
            try:
                send_mail(
                    subject='New Testimonial Submission',
                    message=f'New testimonial submission from {submission.full_name} ({submission.company_name})',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[getattr(settings, 'ADMIN_EMAIL', 'admin@example.com')],
                    fail_silently=True,
                )
            except:
                pass
            
            # Success message for user
            messages.success(request, 'Thank you! Your testimonial has been submitted for review.')
            
            # Redirect to thank you page
            return redirect('thank_you_testimonial')
    else:
        # GET request - display empty form
        form = TestimonialSubmissionForm()
    
    # Get industry choices for form dropdown
    industries = TestimonialSubmission.INDUSTRY_CHOICES
    
    # Prepare context for template
    context = {
        'form': form,  # Form instance
        'industries': industries,  # Industry choices
    }
    
    # Render testimonial submission form
    return render(request, 'testimonials/submit_testimonial.html', context)


def thank_you_testimonial(request):
    """Thank you page after testimonial submission."""
    return render(request, 'testimonials/thank_you.html', {})


@staff_member_required
def approve_testimonials(request):
    """
    Admin-only view to review and approve/reject testimonial submissions.
    
    Features:
        - List pending submissions
        - Approve with conversion to Testimonial model
        - Reject with optional notes
        - Email notifications for both actions
    """
    # Get all pending submissions
    submissions = TestimonialSubmission.objects.filter(status='pending')
    
    if request.method == 'POST':
        # Process approval/rejection action
        submission_id = request.POST.get('submission_id')
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        # Get the specific submission
        submission = get_object_or_404(TestimonialSubmission, id=submission_id)
        
        if action == 'approve':
            # ─── Create Testimonial from Submission ───────────────────────────
            testimonial = Testimonial.objects.create(
                client_name=submission.full_name,
                company=submission.company_name,
                position=submission.position,
                content=submission.testimonial_text,
                industry=submission.industry,
                rating=submission.rating,
                services=submission.services_used,
                is_active=True,  # Make immediately visible
            )
            
            # Copy profile picture if provided
            if submission.profile_picture:
                testimonial.client_image.save(
                    submission.profile_picture.name,
                    submission.profile_picture
                )
            
            # ─── Update Submission Status ─────────────────────────────────────
            submission.status = 'approved'
            submission.approved_testimonial = testimonial
            submission.approved_date = timezone.now()
            submission.admin_notes = notes
            submission.is_public = True
            submission.save()
            
            # ─── Send Approval Email to User ──────────────────────────────────
            try:
                send_mail(
                    subject='Your Testimonial Has Been Published',
                    message=f'''Dear {submission.full_name},
                    
Great news! Your testimonial has been approved and is now published on our website.

Thank you again for sharing your experience. We truly value your feedback.

View your testimonial here: {request.build_absolute_uri('/testimonials')}

Best regards,
Anjali Bansal & Associates''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[submission.email],
                    fail_silently=True,
                )
            except:
                pass
            
            # Success message for admin
            messages.success(request, f'Testimonial from {submission.full_name} approved and published.')
            
        elif action == 'reject':
            # ─── Reject Submission ────────────────────────────────────────────
            submission.status = 'rejected'
            submission.admin_notes = notes
            submission.save()
            
            # ─── Send Rejection Email to User ─────────────────────────────────
            try:
                send_mail(
                    subject='Regarding Your Testimonial Submission',
                    message=f'''Dear {submission.full_name},
                    
Thank you for submitting your testimonial. After careful review, we've decided not to publish it at this time.

{notes if notes else "It doesn't meet our current publishing guidelines."}

We still appreciate your feedback and hope to serve you again in the future.

Best regards,
Anjali Bansal & Associates''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[submission.email],
                    fail_silently=True,
                )
            except:
                pass
            
            # Warning message for admin
            messages.warning(request, f'Testimonial from {submission.full_name} rejected.')
    
    # Prepare context for template
    context = {
        'submissions': submissions,  # All pending submissions
    }
    
    # Render admin approval page
    return render(request, 'admin/approve_testimonials.html', context)


def debug_testimonials(request):
    """
    Debug view to display testimonial and submission data.
    For development/testing purposes only.
    """
    # Get all data for inspection
    testimonials = Testimonial.objects.all()
    submissions = TestimonialSubmission.objects.all()
    
    # Build HTML response with debug information
    html = "<h1>Debug Info</h1>"
    html += "<h2>Testimonials (Published)</h2>"
    html += f"<p>Total: {testimonials.count()}</p>"
    html += "<ul>"
    for t in testimonials:
        html += f"<li>{t.id}: {t.client_name} - {t.company} - Active: {t.is_active}</li>"
    html += "</ul>"
    
    html += "<h2>Testimonial Submissions</h2>"
    html += f"<p>Total: {submissions.count()}</p>"
    html += "<ul>"
    for s in submissions:
        html += f"<li>{s.id}: {s.full_name} - {s.company_name} - Status: {s.status} - Approved Testimonial: {s.approved_testimonial}</li>"
    html += "</ul>"
    
    # Return raw HTML response
    return HttpResponse(html)


# ══════════════════════════════════════════════════════════════════════════════
#                              LEGAL/COMPLIANCE PAGES
# ══════════════════════════════════════════════════════════════════════════════

def privacy_policy(request):
    """Privacy Policy page view."""
    return render(request, 'privacy-policy.html')


def terms_and_conditions(request):
    """Terms and Conditions page view."""
    return render(request, 'terms and conditions.html')


def disclaimer(request):
    """Disclaimer page view."""
    return render(request, 'disclaimer.html')


def refund_policy(request):
    """Refund Policy page view."""
    return render(request, 'refund-policy.html')


# ══════════════════════════════════════════════════════════════════════════════
#                              BOOKING VIEWS
# ══════════════════════════════════════════════════════════════════════════════

def booking(request, duration):
    """
    Consultation booking page view.
    
    Args:
        duration: Duration string (e.g., '30-min', '45-min', '60-min')
    
    Features:
        - Dynamic pricing and feature display based on duration
        - Form handling for booking submissions
        - Email notifications
        - Availability checking
    """
    # Get query parameters for pre-filled data
    plan = request.GET.get('plan', '')
    original_duration = request.GET.get('duration', '')
    price = request.GET.get('price', '')
    
    # ─── Duration Configuration ───────────────────────────────────────────────
    # Define details for each duration option
    duration_details = {
        '30-min': {
            'title': plan or '30-Minute Quick Consultation',
            'price': price or '₹1,000',
            'duration_minutes': '30',
            'price_amount': 1000,
            'features': [
                'One specific compliance query',
                'Basic regulatory guidance',
                'Document review (up to 5 pages)',
                'Email follow-up summary'
            ]
        },
        '45-min': {
            'title': plan or '45-Minute Standard Consultation',
            'price': price or '₹1,500',
            'duration_minutes': '45',
            'price_amount': 1500,
            'features': [
                'Multiple related queries',
                'Detailed regulatory analysis',
                'Document review (up to 15 pages)',
                'Written advice summary',
                '1-week email support'
            ]
        },
        '60-min': {
            'title': plan or '60-Minute Comprehensive Consultation',
            'price': price or '₹2,000',
            'duration_minutes': '60',
            'price_amount': 2000,
            'features': [
                'Complex compliance scenarios',
                'Strategic planning session',
                'Document review (up to 30 pages)',
                'Detailed written recommendations',
                '2-week follow-up support'
            ]
        }
    }
    
    # Get details for the requested duration, default to 45-min if not found
    details = duration_details.get(duration, duration_details['45-min'])
    
    # ─── Handle Form Submission ───────────────────────────────────────────────
    if request.method == 'POST':
        return handle_booking_submission(request, duration, details)
    
    # ─── Prepare Context (GET Request) ────────────────────────────────────────
    context = {
        'duration': duration,  # Selected duration
        'title': details['title'],  # Page title
        'price': details['price'],  # Formatted price
        'price_amount': details['price_amount'],  # Numeric price
        'duration_minutes': details['duration_minutes'],  # Minutes as string
        'features': details['features'],  # List of features
        'referral': request.GET.get('referral', 'service_list_widget'),  # Referral source
        'plan_name': plan,  # Plan name from query
        'original_duration': original_duration  # Original duration parameter
    }
    
    # Render booking form page
    return render(request, 'booking.html', context)


def handle_booking_submission(request, duration, details):
    """
    Handle booking form submission logic.
    
    Args:
        request: HTTP request object
        duration: Selected duration string
        details: Dictionary of booking details
    
    Returns:
        JSON response with success/error status
    """
    try:
        # ─── Parse Appointment Datetime ───────────────────────────────────────
        appointment_datetime = request.POST.get('appointment_datetime')
        if not appointment_datetime:
            return JsonResponse({'success': False, 'error': 'No appointment time selected'})
        
        # Convert ISO format string to datetime object
        dt = datetime.fromisoformat(appointment_datetime)
        
        # Extract duration minutes from string (e.g., '30-min' → 30)
        duration_minutes = int(duration.replace('-min', ''))
        
        # ─── Validate Appointment Time ────────────────────────────────────────
        now = datetime.now()
        
        # Check if date/time is in the past
        if dt < now:
            return JsonResponse({
                'success': False, 
                'error': 'Cannot book appointments in the past. Please select a future date and time.'
            })
        
        # Check if time is available (with 15 min buffer)
        if not is_time_available(dt.date(), dt.time(), duration_minutes):
            return JsonResponse({
                'success': False, 
                'error': 'This time slot is no longer available or overlaps with an existing booking. Please select another time.'
            })
        
        # ─── Create Booking Record ────────────────────────────────────────────
        booking = ConsultationBooking.objects.create(
            duration=duration,
            price=details['price_amount'],
            appointment_date=dt.date(),
            appointment_time=dt.time(),
            mode=request.POST.get('mode', 'video'),
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            company=request.POST.get('company', ''),
            designation=request.POST.get('designation', ''),
            topic=request.POST.get('topic'),
            newsletter_consent=request.POST.get('newsletter') == 'on',
            status='confirmed'  # Auto-confirm for now
        )
        
        # Handle optional document upload
        if 'documents' in request.FILES:
            booking.documents = request.FILES['documents']
            booking.save()
        
        # ─── Log Email Attempt Details ────────────────────────────────────────
        logger.info(f"Attempting to send emails:")
        logger.info(f"  - To client: {booking.email}")
        logger.info(f"  - From: {settings.DEFAULT_FROM_EMAIL}")
        logger.info(f"  - EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        
        # ─── Send Email Notifications ─────────────────────────────────────────
        client_email_sent = send_booking_confirmation_email(booking, details)
        admin_email_sent = send_admin_notification_email(booking, details)
        
        logger.info(f"Booking {booking.booking_id} created. Client email: {client_email_sent}, Admin email: {admin_email_sent}")
        
        # ─── Return Success Response ──────────────────────────────────────────
        return JsonResponse({
            'success': True,
            'booking_id': str(booking.booking_id),
            'client_email': booking.email,
            'admin_email': settings.ADMIN_EMAIL,
            'message': 'Booking confirmed successfully! Check your email for details.'
        })
        
    except Exception as e:
        # ─── Handle Errors ────────────────────────────────────────────────────
        logger.error(f"Error in booking submission: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


# ══════════════════════════════════════════════════════════════════════════════
#                              EMAIL FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def send_booking_confirmation_email(booking, details):
    """
    Send booking confirmation email to client.
    
    Args:
        booking: ConsultationBooking instance
        details: Dictionary of booking details
    
    Returns:
        Boolean indicating success
    """
    try:
        subject = f'Consultation Booking Confirmation - {booking.booking_id}'
        
        # ─── Format Date/Time for Display ────────────────────────────────────
        appointment_date = booking.appointment_date.strftime('%A, %B %d, %Y')
        appointment_time = booking.appointment_time.strftime('%I:%M %p')
        
        # Calculate end time based on duration
        duration_minutes = int(booking.duration.replace('-min', ''))
        start_dt = datetime.combine(booking.appointment_date, booking.appointment_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        end_time = end_dt.strftime('%I:%M %p')
        
        # ─── Create HTML Email Content ────────────────────────────────────────
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .details {{ background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Booking Confirmed!</h1>
                </div>
                <div class="content">
                    <p>Dear {booking.name},</p>
                    <p>Thank you for booking a consultation with Anjali Bansal & Associates. Your appointment has been confirmed.</p>
                    
                    <div class="details">
                        <h3>Appointment Details</h3>
                        <p><strong>Booking ID:</strong> {booking.booking_id}</p>
                        <p><strong>Date:</strong> {appointment_date}</p>
                        <p><strong>Time:</strong> {appointment_time} - {end_time} ({duration_minutes} minutes)</p>
                        <p><strong>Mode:</strong> {booking.get_mode_display()}</p>
                        <p><strong>Duration:</strong> {booking.get_duration_display()}</p>
                        <p><strong>Amount:</strong> ₹{booking.price}</p>
                        <p><strong>Consultation Topic:</strong> {booking.topic[:100]}{'...' if len(booking.topic) > 100 else ''}</p>
                    </div>
                    
                    <h3>Important Notes:</h3>
                    <ul>
                        <li>Please join the meeting 5 minutes before the scheduled time</li>
                        <li>Have your documents ready for discussion</li>
                        <li>Meeting link/details will be sent 1 hour before the appointment</li>
                        <li>You can reschedule up to 24 hours before the appointment</li>
                    </ul>
                    
                    <p>If you need to reschedule or have any questions, please contact us at <a href="mailto:contact@anjali-bansal.com">contact@anjali-bansal.com</a></p>
                    
                    <p>Best regards,<br>
                    <strong>Anjali Bansal & Associates</strong><br>
                    Company Secretaries</p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                    <p>© 2024 Anjali Bansal & Associates. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # ─── Create Plain Text Version ────────────────────────────────────────
        plain_text = f"""Booking Confirmation
========================

Dear {booking.name},

Thank you for booking a consultation with Anjali Bansal & Associates.

APPOINTMENT DETAILS:
Booking ID: {booking.booking_id}
Date: {appointment_date}
Time: {appointment_time} - {end_time} ({duration_minutes} minutes)
Mode: {booking.get_mode_display()}
Duration: {booking.get_duration_display()}
Amount: ₹{booking.price}

IMPORTANT NOTES:
- Please join the meeting 5 minutes before the scheduled time
- Have your documents ready for discussion
- Meeting link/details will be sent 1 hour before the appointment
- You can reschedule up to 24 hours before the appointment

If you need to reschedule or have any questions, please contact us at contact@anjali-bansal.com

Best regards,
Anjali Bansal & Associates
Company Secretaries
"""
        
        # ─── Send Email to Client ─────────────────────────────────────────────
        email_to_client = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email],
        )
        email_to_client.content_subtype = "html"  # Set as HTML email
        email_to_client.send()
        
        logger.info(f"✓ Confirmation email sent to {booking.email} for booking {booking.booking_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error sending confirmation email for booking {booking.booking_id}: {str(e)}")
        # Don't fail the booking if email fails
        return False


def send_admin_notification_email(booking, details):
    """
    Send booking notification email to admin.
    
    Args:
        booking: ConsultationBooking instance
        details: Dictionary of booking details
    
    Returns:
        Boolean indicating success
    """
    try:
        subject = f'📅 New Booking: {booking.name} - {booking.appointment_date}'
        
        # Calculate end time for admin reference
        duration_minutes = int(booking.duration.replace('-min', ''))
        start_dt = datetime.combine(booking.appointment_date, booking.appointment_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # Create detailed plain text message for admin
        message = f"""
        NEW CONSULTATION BOOKING
        
        Booking ID: {booking.booking_id}
        Booking Time: {booking.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        
        CLIENT INFORMATION:
        Name: {booking.name}
        Email: {booking.email}
        Phone: {booking.phone}
        Company: {booking.company or 'N/A'}
        Designation: {booking.designation or 'N/A'}
        
        APPOINTMENT DETAILS:
        Date: {booking.appointment_date}
        Time: {booking.appointment_time.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}
        Duration: {booking.get_duration_display()}
        Mode: {booking.get_mode_display()}
        Amount: ₹{booking.price}
        
        CONSULTATION TOPIC:
        {booking.topic}
        
        ADDITIONAL NOTES:
        Newsletter Consent: {'Yes' if booking.newsletter_consent else 'No'}
        
        ---
        This is an automated notification from the booking system.
        """
        
        # Send email to admin
        admin_email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL]  # Use ADMIN_EMAIL from settings
        )
        admin_email.send()
        
        logger.info(f"✓ Admin notification sent for booking {booking.booking_id}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error sending admin notification: {str(e)}")
        return False


def send_cancellation_email(booking, reason=None):
    """
    Send cancellation email to client.
    
    Args:
        booking: ConsultationBooking instance
        reason: Optional cancellation reason
    
    Returns:
        Boolean indicating success
    """
    try:
        subject = f'Consultation Booking Cancelled - {booking.booking_id}'
        
        # ─── Format Date/Time for Display ────────────────────────────────────
        appointment_date = booking.appointment_date.strftime('%A, %B %d, %Y')
        appointment_time = booking.appointment_time.strftime('%I:%M %p')
        
        # Calculate end time
        duration_minutes = int(booking.duration.replace('-min', ''))
        start_dt = datetime.combine(booking.appointment_date, booking.appointment_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        end_time = end_dt.strftime('%I:%M %p')
        
        # Use provided reason or fall back to booking's reason
        cancellation_reason = reason or booking.cancellation_reason or "due to unforeseen circumstances"
        
        # ─── Create HTML Email Content ────────────────────────────────────────
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .details {{ background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
                .cancellation-reason {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
                .action-buttons {{ margin: 20px 0; text-align: center; }}
                .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
                .btn-reschedule {{ background-color: #28a745; }}
                .btn-contact {{ background-color: #17a2b8; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Booking Cancelled</h1>
                </div>
                <div class="content">
                    <p>Dear {booking.name},</p>
                    <p>We regret to inform you that your consultation booking with Anjali Bansal & Associates has been cancelled.</p>
                    
                    <div class="details">
                        <h3>Cancelled Appointment Details</h3>
                        <p><strong>Booking ID:</strong> {booking.booking_id}</p>
                        <p><strong>Original Date:</strong> {appointment_date}</p>
                        <p><strong>Original Time:</strong> {appointment_time} - {end_time} ({duration_minutes} minutes)</p>
                        <p><strong>Duration:</strong> {booking.get_duration_display()}</p>
                        <p><strong>Mode:</strong> {booking.get_mode_display()}</p>
                        <p><strong>Amount:</strong> ₹{booking.price}</p>
                    </div>
                    
                    <div class="cancellation-reason">
                        <h4>Cancellation Reason:</h4>
                        <p>{cancellation_reason}</p>
                    </div>
                    
                    <div class="action-buttons">
                        <a href="https://anjali-bansal.com/services" class="btn btn-reschedule">Reschedule Appointment</a>
                        <a href="mailto:contact@anjali-bansal.com" class="btn btn-contact">Contact Support</a>
                    </div>
                    
                    <h3>Next Steps:</h3>
                    <ul>
                        <li>You can book a new appointment through our <a href="https://anjali-bansal.com/services">services page</a></li>
                        <li>If you have any questions, please contact us at <a href="mailto:contact@anjali-bansal.com">contact@anjali-bansal.com</a></li>
                        <li>For refund inquiries, please email <a href="mailto:billing@anjali-bansal.com">billing@anjali-bansal.com</a></li>
                        <li>We apologize for any inconvenience caused and hope to assist you in the future</li>
                    </ul>
                    
                    <p>Best regards,<br>
                    <strong>Anjali Bansal & Associates</strong><br>
                    Company Secretaries</p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                    <p>© {datetime.now().year} Anjali Bansal & Associates. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # ─── Send Email to Client ─────────────────────────────────────────────
        email_to_client = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email],
        )
        email_to_client.content_subtype = "html"
        email_to_client.send()
        
        logger.info(f"✓ Cancellation email sent to {booking.email} for booking {booking.booking_id}")
        
        # Also notify admin about cancellation
        send_admin_cancellation_notification(booking, cancellation_reason)
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error sending cancellation email for booking {booking.booking_id}: {str(e)}")
        return False


def send_admin_cancellation_notification(booking, reason):
    """
    Send cancellation notification email to admin.
    
    Args:
        booking: ConsultationBooking instance
        reason: Cancellation reason
    
    Returns:
        Boolean indicating success
    """
    try:
        subject = f'⚠️ Booking Cancelled: {booking.name} - {booking.booking_id}'
        
        # Create detailed message for admin
        message = f"""
        BOOKING CANCELLATION NOTIFICATION
        
        Cancelled Booking ID: {booking.booking_id}
        Cancellation Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        CLIENT INFORMATION:
        Name: {booking.name}
        Email: {booking.email}
        Phone: {booking.phone}
        Company: {booking.company or 'N/A'}
        
        ORIGINAL APPOINTMENT DETAILS:
        Date: {booking.appointment_date}
        Time: {booking.appointment_time.strftime('%H:%M')}
        Duration: {booking.get_duration_display()}
        Mode: {booking.get_mode_display()}
        Amount: ₹{booking.price}
        
        CANCELLATION REASON:
        {reason}
        
        BOOKING HISTORY:
        Created: {booking.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        Confirmed: {booking.confirmed_at.strftime('%Y-%m-%d %H:%M:%S') if booking.confirmed_at else 'N/A'}
        Cancelled: {booking.cancelled_at.strftime('%Y-%m-%d %H:%M:%S') if booking.cancelled_at else 'N/A'}
        
        ---
        This is an automated notification from the booking system.
        """
        
        # Send email to admin
        admin_email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL]
        )
        admin_email.send()
        
        logger.info(f"✓ Admin cancellation notification sent for booking {booking.booking_id}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error sending admin cancellation notification: {str(e)}")
        return False


def send_status_change_email(booking, new_status, old_status=None):
    """
    Send email notification when booking status changes.
    
    Args:
        booking: ConsultationBooking instance
        new_status: New status value
        old_status: Previous status value (optional)
    
    Returns:
        Boolean indicating success
    """
    try:
        # Status display mapping for user-friendly text
        status_display = {
            'pending': 'Pending Review',
            'confirmed': 'Confirmed',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        
        # ─── Format Date/Time for Display ────────────────────────────────────
        appointment_date = booking.appointment_date.strftime('%A, %B %d, %Y')
        appointment_time = booking.appointment_time.strftime('%I:%M %p')
        
        # Calculate end time
        duration_minutes = int(booking.duration.replace('-min', ''))
        start_dt = datetime.combine(booking.appointment_date, booking.appointment_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        end_time = end_dt.strftime('%I:%M %p')
        
        # Email subject
        subject = f'Booking Status Update - {status_display[new_status]} - {booking.booking_id}'
        
        # ─── Configure Email Content Based on Status ──────────────────────────
        # ALWAYS SEND EMAIL FOR STATUS CHANGE, REGARDLESS OF PREVIOUS STATUS
        
        if new_status == 'pending':
            status_color = '#ffc107'  # Yellow
            status_icon = '⏳'
            title = 'Booking Under Review'
            message = f"""Your booking is now <strong>Under Review</strong>."""
            instructions = """
            <p><strong>What happens next?</strong></p>
            <ul>
                <li>We're reviewing your booking request</li>
                <li>You'll receive a confirmation email once approved</li>
                <li>No action is required from you at this time</li>
            </ul>
            """
            
        elif new_status == 'confirmed':
            status_color = '#28a745'  # Green
            status_icon = '✅'
            title = 'Booking Confirmed!'
            message = f"""Your booking has been <strong>Confirmed</strong>."""
            instructions = """
            <p><strong>Important Notes:</strong></p>
            <ul>
                <li>Please join the meeting 5 minutes before the scheduled time</li>
                <li>Have your documents ready for discussion</li>
                <li>Meeting link/details will be sent 1 hour before the appointment</li>
                <li>You can reschedule up to 24 hours before the appointment</li>
            </ul>
            """
            
        elif new_status == 'completed':
            status_color = '#17a2b8'  # Teal
            status_icon = '🏁'
            title = 'Consultation Completed'
            message = f"""Your consultation has been marked as <strong>Completed</strong>."""
            instructions = """
            <p><strong>Thank you for your consultation!</strong></p>
            <ul>
                <li>We hope you found the session valuable</li>
                <li>Please don't hesitate to reach out if you have follow-up questions</li>
                <li>Consider leaving a testimonial about your experience</li>
            </ul>
            """
            # Add feedback request section
            instructions += """
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h4>📝 Share Your Experience</h4>
                <p>We value your feedback! Please consider sharing your experience:</p>
                <a href="https://anjali-bansal.com/testimonials/submit/" 
                   style="display: inline-block; background: #007bff; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 5px; margin-top: 10px;">
                   Submit Testimonial
                </a>
            </div>
            """
            
        elif new_status == 'cancelled':
            status_color = '#dc3545'  # Red
            status_icon = '❌'
            title = 'Booking Cancelled'
            message = f"""Your booking has been <strong>Cancelled</strong>."""
            cancellation_reason = booking.cancellation_reason or "due to unforeseen circumstances"
            instructions = f"""
            <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                <h4>Cancellation Reason:</h4>
                <p>{cancellation_reason}</p>
            </div>
            <p><strong>Next Steps:</strong></p>
            <ul>
                <li>You can book a new appointment through our <a href="https://anjali-bansal.com/services">services page</a></li>
                <li>If you have any questions, please contact us</li>
            </ul>
            """
        else:
            # Default for unknown status
            status_color = '#6c757d'  # Gray
            status_icon = 'ℹ️'
            title = f'Booking Status Updated'
            message = f"""Your booking status has been updated to <strong>{status_display[new_status]}</strong>."""
            instructions = ""
        
        # ─── Add Status Change Note (if old_status provided) ──────────────────
        status_change_note = ""
        if old_status and old_status != new_status:
            status_change_note = f"""
            <div style="background: #e9ecef; padding: 10px; border-radius: 5px; margin: 10px 0; font-size: 14px;">
                <strong>Status Changed:</strong> {status_display[old_status]} → {status_display[new_status]}
            </div>
            """
        
        # ─── Create HTML Email Content ────────────────────────────────────────
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: {status_color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .details {{ background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
                .status-badge {{ display: inline-block; background: {status_color}; color: white; 
                                padding: 5px 10px; border-radius: 3px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{status_icon} {title}</h1>
                </div>
                <div class="content">
                    <p>Dear {booking.name},</p>
                    <p>{message}</p>
                    
                    {status_change_note}
                    
                    <div class="details">
                        <h3>Appointment Details</h3>
                        <p><strong>Booking ID:</strong> {booking.booking_id}</p>
                        <p><strong>Status:</strong> <span class="status-badge">{status_display[new_status]}</span></p>
                        <p><strong>Date:</strong> {appointment_date}</p>
                        <p><strong>Time:</strong> {appointment_time} - {end_time} ({duration_minutes} minutes)</p>
                        <p><strong>Mode:</strong> {booking.get_mode_display()}</p>
                        <p><strong>Topic:</strong> {booking.topic[:100]}{'...' if len(booking.topic) > 100 else ''}</p>
                    </div>
                    
                    {instructions}
                    
                    <p>If you have any questions about this status change, please contact us at 
                       <a href="mailto:contact@anjali-bansal.com">contact@anjali-bansal.com</a></p>
                    
                    <p>Best regards,<br>
                    <strong>Anjali Bansal & Associates</strong><br>
                    Company Secretaries</p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                    <p>© {datetime.now().year} Anjali Bansal & Associates. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # ─── Send Status Change Email ─────────────────────────────────────────
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email],
        )
        email.content_subtype = "html"
        email.send()
        
        logger.info(f"✓ Status change email sent to {booking.email} - Status: {old_status} → {new_status}")
        
        # Also notify admin about status change
        send_admin_status_notification(booking, new_status, old_status)
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error sending status change email for booking {booking.booking_id}: {str(e)}")
        return False


def send_admin_status_notification(booking, new_status, old_status):
    """
    Send status change notification email to admin.
    
    Args:
        booking: ConsultationBooking instance
        new_status: New status value
        old_status: Previous status value
    
    Returns:
        Boolean indicating success
    """
    try:
        # Status display mapping
        status_display = {
            'pending': 'Pending',
            'confirmed': 'Confirmed',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        
        subject = f'📊 Status Changed: {booking.name} - {status_display[new_status]}'
        
        # Create detailed message for admin
        message = f"""
        BOOKING STATUS CHANGE NOTIFICATION
        
        Booking ID: {booking.booking_id}
        Status Changed: {status_display[old_status]} → {status_display[new_status]}
        Change Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        CLIENT INFORMATION:
        Name: {booking.name}
        Email: {booking.email}
        Phone: {booking.phone}
        Company: {booking.company or 'N/A'}
        
        APPOINTMENT DETAILS:
        Date: {booking.appointment_date}
        Time: {booking.appointment_time.strftime('%H:%M')}
        Duration: {booking.get_duration_display()}
        Mode: {booking.get_mode_display()}
        Amount: ₹{booking.price}
        
        BOOKING HISTORY:
        Created: {booking.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        Pending: {booking.pending_at.strftime('%Y-%m-%d %H:%M:%S') if booking.pending_at else 'N/A'}
        Confirmed: {booking.confirmed_at.strftime('%Y-%m-%d %H:%M:%S') if booking.confirmed_at else 'N/A'}
        Completed: {booking.completed_at.strftime('%Y-%m-%d %H:%M:%S') if booking.completed_at else 'N/A'}
        Cancelled: {booking.cancelled_at.strftime('%Y-%m-%d %H:%M:%S') if booking.cancelled_at else 'N/A'}
        
        ---
        This is an automated notification from the booking system.
        """
        
        # Send email to admin
        admin_email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL]
        )
        admin_email.send()
        
        logger.info(f"✓ Admin status change notification sent for booking {booking.booking_id}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error sending admin status change notification: {str(e)}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
#                              ADMIN BOOKING MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

@staff_member_required
def admin_booking_management(request):
    """
    Admin dashboard for managing all bookings.
    
    Features:
        - Status filtering
        - Date filtering
        - Booking statistics
        - List view with pagination
    """
    # ─── Get Query Parameters for Filtering ───────────────────────────────────
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    # Start with all bookings, ordered by creation date (newest first)
    bookings = ConsultationBooking.objects.all().order_by('-created_at')
    
    # ─── Apply Filters ────────────────────────────────────────────────────────
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            bookings = bookings.filter(appointment_date=date_obj)
        except ValueError:
            pass  # Invalid date format, ignore filter
    
    # ─── Calculate Statistics ─────────────────────────────────────────────────
    total_bookings = ConsultationBooking.objects.count()
    confirmed_bookings = ConsultationBooking.objects.filter(status='confirmed').count()
    pending_bookings = ConsultationBooking.objects.filter(status='pending').count()
    cancelled_bookings = ConsultationBooking.objects.filter(status='cancelled').count()
    completed_bookings = ConsultationBooking.objects.filter(status='completed').count()
    
    # ─── Prepare Context ──────────────────────────────────────────────────────
    context = {
        'bookings': bookings,  # Filtered booking list
        'status_filter': status_filter,  # Current status filter
        'date_filter': date_filter,  # Current date filter
        'today': date.today(),  # Current date for reference
        'stats': {
            'total': total_bookings,
            'confirmed': confirmed_bookings,
            'pending': pending_bookings,
            'cancelled': cancelled_bookings,
            'completed': completed_bookings,
        }
    }
    
    # Render admin booking management page
    return render(request, 'admin/booking_management.html', context)


@staff_member_required
def admin_cancel_booking(request, booking_id):
    """
    Admin view to cancel a specific booking.
    
    Args:
        booking_id: UUID of the booking to cancel
    """
    # Get the specific booking
    booking = get_object_or_404(ConsultationBooking, booking_id=booking_id)
    
    if request.method == 'POST':
        # Get cancellation reason from form
        reason = request.POST.get('reason', '')
        
        # Update booking status
        booking.status = 'cancelled'
        booking.cancellation_reason = reason
        booking.cancelled_at = timezone.now()
        booking.save()
        
        # Send cancellation email to client
        send_cancellation_email(booking, reason)
        send_admin_status_notification(booking, 'cancelled', 'confirmed')
        
        # Success message and redirect
        messages.success(request, f'Booking {booking_id} has been cancelled and notification sent to client.')
        return redirect('admin_booking_management')
    
    # GET request - show cancellation form
    context = {
        'booking': booking,
    }
    
    # Render cancellation confirmation page
    return render(request, 'admin/cancel_booking.html', context)


@staff_member_required
def admin_complete_booking(request, booking_id):
    """
    Admin view to mark a booking as completed.
    
    Args:
        booking_id: UUID of the booking to mark as completed
    """
    # Get the specific booking
    booking = get_object_or_404(ConsultationBooking, booking_id=booking_id)
    
    if request.method == 'POST':
        # Store old status for notification
        old_status = booking.status
        
        # Update booking status
        booking.status = 'completed'
        booking.completed_at = timezone.now()
        booking.save()
        
        # Send completion notification to client
        send_status_change_email(booking, 'completed', old_status)
        send_admin_status_notification(booking, 'completed', old_status)
        
        # Success message and redirect
        messages.success(request, f'Booking {booking_id} has been marked as completed and notification sent to client.')
        return redirect('admin_booking_management')
    
    # GET request - show completion confirmation form
    context = {
        'booking': booking,
    }
    
    # Render completion confirmation page
    return render(request, 'admin/complete_booking.html', context)


@staff_member_required
def admin_mark_pending(request, booking_id):
    """
    Admin view to mark a booking as pending.
    
    Args:
        booking_id: UUID of the booking to mark as pending
    """
    # Get the specific booking
    booking = get_object_or_404(ConsultationBooking, booking_id=booking_id)
    
    if request.method == 'POST':
        # Store old status for notification
        old_status = booking.status
        
        # Update booking status
        booking.status = 'pending'
        booking.pending_at = timezone.now()
        booking.save()
        
        # Send pending notification to client
        send_status_change_email(booking, 'pending', old_status)
        send_admin_status_notification(booking, 'pending', old_status)
        
        # Success message and redirect
        messages.success(request, f'Booking {booking_id} has been marked as pending and notification sent to client.')
        return redirect('admin_booking_management')
    
    # GET request - show pending confirmation form
    context = {
        'booking': booking,
    }
    
    # Render pending confirmation page
    return render(request, 'admin/mark_pending.html', context)


# ══════════════════════════════════════════════════════════════════════════════
#                              API ENDPOINTS FOR BOOKING
# ══════════════════════════════════════════════════════════════════════════════

def get_available_slots(request):
    """
    API endpoint to get available time slots for a specific date.
    
    Query Parameters:
        - date: Date in YYYY-MM-DD format
        - duration: Duration in minutes (default: 45)
    
    Returns:
        JSON response with available slots
    """
    # ─── Parse Query Parameters ───────────────────────────────────────────────
    selected_date = request.GET.get('date')
    duration = request.GET.get('duration', '45')  # Default to 45 minutes
    
    # Validate required parameters
    if not selected_date:
        return JsonResponse({'error': 'No date provided'}, status=400)
    
    try:
        # Convert string date to date object
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Check if date is in the past
    if selected_date_obj < date.today():
        return JsonResponse({
            'date': selected_date,
            'duration': duration,
            'available_slots': []  # No slots for past dates
        })
    
    # ─── Configure Time Parameters ────────────────────────────────────────────
    # Convert duration to integer
    duration_minutes = int(duration)
    
    # Define working hours (9 AM to 5 PM)
    start_hour = 9
    end_hour = 17
    
    # Get current time for checking today's availability
    now = datetime.now()
    is_today = selected_date_obj == now.date()
    
    # Get all non-cancelled bookings for the selected date
    bookings = ConsultationBooking.objects.filter(
        appointment_date=selected_date_obj
    ).exclude(status='cancelled').order_by('appointment_time')
    
    # ─── Generate Available Slots ─────────────────────────────────────────────
    available_slots = []
    
    # Start from beginning of day at 9:00 AM
    current_time = datetime.combine(selected_date_obj, datetime.min.time())
    current_time = current_time.replace(hour=start_hour, minute=0)
    end_time = current_time.replace(hour=end_hour, minute=0)
    
    # Convert duration to timedelta for calculations
    duration_td = timedelta(minutes=duration_minutes)
    
    # Generate slots every 15 minutes within working hours
    while current_time.time() <= end_time.time():
        slot_end = current_time + duration_td
        
        # Skip past time slots for today
        if is_today and current_time.time() < now.time():
            current_time += timedelta(minutes=15)
            continue
        
        # Check if slot ends before working hours end
        if slot_end.time() <= end_time.time():
            # Check for overlap with existing bookings (with 15 min buffer)
            is_available = True
            
            for booking in bookings:
                booking_start = datetime.combine(selected_date_obj, booking.appointment_time)
                booking_duration = timedelta(minutes=int(booking.duration.replace('-min', '')))
                booking_end = booking_start + booking_duration + timedelta(minutes=15)  # Add 15 min buffer
                
                # Check for time overlap
                if (current_time < booking_end and slot_end > booking_start):
                    is_available = False
                    break
            
            if is_available:
                # Generate a unique slot ID
                slot_id = f"{selected_date.replace('-', '')}{current_time.hour:02d}{current_time.minute:02d}"
                
                available_slots.append({
                    'id': slot_id,
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': slot_end.strftime('%H:%M'),
                    'duration': str(duration_minutes),
                    'max_bookings': 1,  # Each slot is unique
                    'available': 1,
                    'display': f"{current_time.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}"
                })
        
        # Move to next 15-minute interval
        current_time += timedelta(minutes=15)
    
    # ─── Return JSON Response ─────────────────────────────────────────────────
    return JsonResponse({
        'date': selected_date,
        'duration': duration,
        'available_slots': available_slots,
        'working_hours': f"{start_hour}:00 - {end_hour}:00",
        'is_today': is_today,
        'current_time': now.strftime('%H:%M') if is_today else None
    })


def check_date_availability(request):
    """
    API endpoint to check which dates have available slots in a month.
    
    Query Parameters:
        - year: Year (default: current year)
        - month: Month (1-12, default: current month)
        - duration: Duration in minutes (default: 45)
    
    Returns:
        JSON response with availability for each date in the month
    """
    # ─── Parse Query Parameters ───────────────────────────────────────────────
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    duration = request.GET.get('duration', '45')
    
    # ─── Calculate Month Boundaries ───────────────────────────────────────────
    start_date = date(year, month, 1)  # First day of month
    
    # Last day of month (first day of next month minus 1 day)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    # ─── Check Availability for Each Date ─────────────────────────────────────
    dates = []
    current_date = start_date
    
    # Iterate through all dates in the month
    while current_date < end_date:
        # Skip past dates
        if current_date < date.today():
            dates.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day': current_date.day,
                'has_availability': False,
                'is_past': True
            })
        else:
            # Check if this date has any available slots
            has_availability = False
            
            # Check every 15 minutes within working hours (9 AM to 5 PM)
            for hour in range(9, 17):
                for minute in [0, 15, 30, 45]:
                    check_time = time(hour, minute)
                    
                    # Calculate if slot fits in working hours
                    duration_minutes = int(duration)
                    duration_td = timedelta(minutes=duration_minutes)
                    start_dt = datetime.combine(current_date, check_time)
                    end_dt = start_dt + duration_td
                    
                    # Slot must end before 5 PM
                    if end_dt.time() <= time(17, 0):
                        # Check if time is available
                        if is_time_available(current_date, check_time, duration_minutes):
                            has_availability = True
                            break  # Found one available slot, no need to check further
                
                if has_availability:
                    break  # Date has availability, move to next date
            
            # Add date to results
            dates.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day': current_date.day,
                'has_availability': has_availability,
                'is_past': False
            })
        
        # Move to next day
        current_date += timedelta(days=1)
    
    # ─── Return JSON Response ─────────────────────────────────────────────────
    return JsonResponse({
        'year': year,
        'month': month,
        'duration': duration,
        'dates': dates
    })


# ══════════════════════════════════════════════════════════════════════════════
#                              HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def is_time_available(date_obj, start_time, duration_minutes):
    """
    Check if a specific time slot is available.
    
    Args:
        date_obj: Date object to check
        start_time: Time object for start time
        duration_minutes: Duration in minutes
    
    Returns:
        Boolean: True if time slot is available, False otherwise
    """
    # Calculate requested start and end times
    requested_start = datetime.combine(date_obj, start_time)
    requested_end = requested_start + timedelta(minutes=duration_minutes)
    
    # Get all non-cancelled bookings for this date
    bookings = ConsultationBooking.objects.filter(
        appointment_date=date_obj
    ).exclude(status='cancelled')
    
    # Check for overlap with each existing booking
    for booking in bookings:
        booking_start = datetime.combine(date_obj, booking.appointment_time)
        booking_duration = timedelta(minutes=int(booking.duration.replace('-min', '')))
        booking_end = booking_start + booking_duration + timedelta(minutes=15)  # Add 15 min buffer
        
        # Check if time intervals overlap
        if (requested_start < booking_end and requested_end > booking_start):
            return False  # Time slot is not available
    
    return True  # Time slot is available


# ══════════════════════════════════════════════════════════════════════════════
#                                  END OF VIEWS
# ══════════════════════════════════════════════════════════════════════════════