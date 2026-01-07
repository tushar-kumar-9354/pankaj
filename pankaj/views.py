
# ══════════════════════════════════════════════════════════════════════════════
#                                   IMPORTS
# ══════════════════════════════════════════════════════════════════════════════

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
from django.core.cache import cache  # For caching
from django.db.models import Avg  # For average calculation

# Standard Library Imports
from datetime import datetime, timedelta, date  # Date/time manipulation
import time as time_module  # Rename time module to avoid conflict
import logging  # Application logging

# Application-Specific Imports
from .models import BlogPost, Testimonial, ConsultationBooking, TimeSlotManager
# Comment out TestimonialSubmission import since we're hiding user submission
# from .forms import TestimonialSubmissionForm  # Form for testimonial submissions
# Application-Specific Imports
# Comment out TestimonialSubmission import since we're hiding user submission
# from .forms import TestimonialSubmissionForm  # Form for testimonial submissions

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
    latest_blogs = BlogPost.objects.filter(is_published=True).order_by('-date_published')[:3]
    
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
    """
    # Start with all published blog posts
    all_blogs = BlogPost.objects.filter(is_published=True)
    
    # Filter out posts with empty or invalid slugs
    all_blogs = [blog for blog in all_blogs if blog.slug and str(blog.slug).strip() != '']
    
    # ─── Category Filtering ────────────────────────────────────────────────────
    category_filter = request.GET.get('category')
    
    # Apply category filter if specified (exact match)
    if category_filter:
        all_blogs = [blog for blog in all_blogs if blog.category == category_filter]
    
    # ─── Get Distinct Categories ───────────────────────────────────────────────
    categories = list(set([blog.category for blog in BlogPost.objects.filter(is_published=True) if blog.slug and str(blog.slug).strip() != '']))
    categories.sort()
    
    # ─── Sorting ───────────────────────────────────────────────────────────────
    sort_by = request.GET.get('sort', 'latest')
    
    # Apply sorting based on user selection
    if sort_by == 'oldest':
        all_blogs.sort(key=lambda x: x.date_published)
    elif sort_by == 'popular':
        all_blogs.sort(key=lambda x: x.read_time, reverse=True)
    else:  # Default to 'latest'
        all_blogs.sort(key=lambda x: x.date_published, reverse=True)
    
    # ─── Pagination ────────────────────────────────────────────────────────────
    # Split results into pages (3 posts per page)
    paginator = Paginator(all_blogs, 3)
    
    # Get current page number from query parameters
    page_number = request.GET.get('page')
    
    # Get page object for current page
    page_obj = paginator.get_page(page_number)
    
    # ─── Prepare Context ───────────────────────────────────────────────────────
    return render(request, "blogs.html", {
        'blogs': page_obj,
        'categories': categories,
        'current_category': category_filter,
        'current_sort': sort_by,
        'page_obj': page_obj,
    })

def blog_detail(request, slug):
    """
    Individual blog post detail view with enhanced features.
    """
    # Get the specific blog post by slug, ensure it's published
    blog = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment view count
    blog.increment_view_count()
    
    # Get related posts from the same category (excluding current post)
    related_posts = BlogPost.objects.filter(
        category=blog.category, 
        is_published=True
    ).exclude(id=blog.id)[:3]
    
    # Get ACTUAL categories from existing published blogs only
    all_published_blogs = BlogPost.objects.filter(is_published=True)
    categories = list(set([blog.category for blog in all_published_blogs 
                         if blog.category and blog.slug and str(blog.slug).strip() != '']))
    categories.sort()
    
    # Get featured posts (excluding current post)
    # First try to get actual featured posts
    featured_posts = BlogPost.objects.filter(
        is_published=True,
        is_featured=True
    ).exclude(id=blog.id)[:3]
    
    # If no featured posts, show latest posts instead
    if not featured_posts:
        featured_posts = BlogPost.objects.filter(
            is_published=True
        ).exclude(id=blog.id).order_by('-date_published')[:3]
    
    # Prepare context for template
    context = {
        'blog': blog,
        'related_posts': related_posts,
        'categories': categories,
        'featured_posts': featured_posts,  # This will always have posts
        'current_category': blog.category,
    }
    
    return render(request, "blog_detail.html", context)


from .models import BlogPost


# ══════════════════════════════════════════════════════════════════════════════
#                              TESTIMONIAL VIEWS - COMMENTED OUT
# ══════════════════════════════════════════════════════════════════════════════

"""
# COMMENTED OUT: User testimonial submission functionality
# Admin can still add testimonials via admin panel

def testimonials(request):
    ""
    Main testimonials page with industry filtering and statistics.
    
    Features:
        - Industry-based tabbed organization
        - Featured testimonials slider
        - Video testimonials section
        - Statistics dashboard
        - Admin notification for pending submissions
    ""
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
        'industries_served': len(industries),
        'client_satisfaction': 98,  # Count of unique industries
    }
    
    # ─── Video Testimonials ───────────────────────────────────────────────────
    # Get testimonials with video URLs
   
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
         # Video testimonials
        'pending_submissions': pending_submissions,  # Admin-only data
    }
    
    # Render testimonials template
    return render(request, "testimonials.html", context)


def submit_testimonial(request):
    ""
    View for users to submit new testimonials.
    
    Handles:
        - Form display (GET)
        - Form submission (POST)
        - Email notifications (user confirmation, admin alert)
    ""
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
                    subject='Testimonial Submission Received - KP RegTech',
                    message=f'''Dear {submission.full_name},
                    
Thank you for submitting your testimonial! We truly appreciate you taking the time to share your experience.

Your submission is now under review. We'll notify you once it's approved and published on our website.

If you have any questions, please don't hesitate to contact us.

Best regards,
KP RegTech''',
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
                    message=f'New testimonial submission from {submission.full_name} ({submission.company})',
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
    industries = TestimonialSubmission.industry
    
    # Prepare context for template
    context = {
        'form': form,  # Form instance
        'industries': industries,  # Industry choices
    }
    
    # Render testimonial submission form
    return render(request, 'testimonials/submit_testimonial.html', context)


def thank_you_testimonial(request):
    "Thank you page after testimonial submission."
    return render(request, 'testimonials/thank_you.html', {})


@staff_member_required
def approve_testimonials(request):
    ""
    Admin-only view to review and approve/reject testimonial submissions.
    
    Features:
        - List pending submissions
        - Approve with conversion to Testimonial model
        - Reject with optional notes
        - Email notifications for both actions
    ""
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
                company=submission.company,
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
KP RegTech''',
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
KP RegTech''',
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
    ""
    Debug view to display testimonial and submission data.
    For development/testing purposes only.
    ""
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
        html += f"<li>{s.id}: {s.full_name} - {s.company} - Status: {s.status} - Approved Testimonial: {s.approved_testimonial}</li>"
    html += "</ul>"
    
    # Return raw HTML response
    return HttpResponse(html)
"""

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

# ... [Rest of the file remains exactly the same - booking views, email functions, etc.] ...

# Note: The rest of the file (booking views, payment views, etc.) remains unchanged
# Only testimonial-related views are commented out above
# ══════════════════════════════════════════════════════════════════════════════
#                              BOOKING VIEWS
# ══════════════════════════════════════════════════════════════════════════════
def booking(request, duration):
    """Consultation booking page view."""
    
    logger.info(f"Booking view called with duration: {duration}")
    logger.info(f"Request method: {request.method}")
    
    # Duration configuration
    duration_details = {
        '30-min': {
            'title': '30-Minute Quick Consultation',
            'price': '₹1,000',
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
            'title': '45-Minute Standard Consultation',
            'price': '₹1,500',
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
            'title': '60-Minute Comprehensive Consultation',
            'price': '₹2,000',
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
    
    # Get details for the requested duration
    details = duration_details.get(duration, duration_details['45-min'])
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        # Ensure JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return handle_booking_submission(request, duration, details)
        else:
            # Handle regular form submission
            result = handle_booking_submission(request, duration, details)
            return result
    
    # GET request - show booking form
    context = {
        'duration': duration,
        'title': details['title'],
        'price': details['price'],
        'price_amount': details['price_amount'],
        'duration_minutes': details['duration_minutes'],
        'features': details['features'],
    }
    
    return render(request, 'booking.html', context)
# In views.py, update handle_booking_submission function:



def handle_booking_submission(request, duration, details):
    """Handle booking form submission with robust duplicate prevention"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        print("=== NEW BOOKING SUBMISSION START ===")
        print(f"Request path: {request.path}")
        print(f"Request method: {request.method}")
        
        # Parse data
        selected_date = request.POST.get('selected_date')
        selected_time = request.POST.get('selected_time')
        
        print(f"Selected date: {selected_date}, Selected time: {selected_time}")
        
        if not selected_date or not selected_time:
            print("Error: No appointment time selected")
            return JsonResponse({'success': False, 'error': 'No appointment time selected'})
        
        # Create datetime
        dt_str = f"{selected_date} {selected_time}"
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
        
        # Check if date/time is in the past
        now = datetime.now()
        if dt < now:
            print("Error: Cannot book appointments in the past")
            return JsonResponse({
                'success': False, 
                'error': 'Cannot book appointments in the past.'
            })
        
        # Extract duration minutes
        duration_minutes = int(duration.replace('-min', ''))
        
        # Get form data
        client_email = request.POST.get('email')
        client_name = request.POST.get('name')
        
        # Create a unique request fingerprint
        request_fingerprint = f"{client_email}_{selected_date}_{selected_time}_{time_module.time()}"
        
        # Check for duplicate submission using session
        session_key = f'booking_submission_{request_fingerprint}'
        if request.session.get(session_key):
            print(f"Duplicate submission detected for {client_email}")
            return JsonResponse({
                'success': False,
                'error': 'Duplicate submission detected. Please wait.'
            })
        
        # Mark this submission in session (expires in 30 seconds)
        request.session[session_key] = True
        request.session.set_expiry(30)
        
        # Check for existing booking with same email, date, and time (last 5 minutes)
        five_minutes_ago = now - timedelta(minutes=5)
        existing_booking = ConsultationBooking.objects.filter(
            email=client_email,
            appointment_date=dt.date(),
            appointment_time=dt.time(),
            created_at__gte=five_minutes_ago
        ).first()
        
        if existing_booking:
            print(f"Existing booking found: {existing_booking.booking_id}")
            return JsonResponse({
                'success': True,
                'booking_id': str(existing_booking.booking_id),
                'redirect_url': f'/admin/pankaj/consultationbooking/',
                'message': 'Booking already exists. Redirecting to admin page.'
            })
        
        print(f"Creating NEW booking for: {client_name}")
        
        # Create Booking Record with timezone-aware datetime
        booking = ConsultationBooking.objects.create(
            duration=duration,
            price=details['price_amount'],
            appointment_date=dt.date(),
            appointment_time=dt.time(),
            mode=request.POST.get('mode', 'video'),
            name=client_name,
            email=client_email,
            phone=request.POST.get('phone'),
            company=request.POST.get('company', ''),
            designation=request.POST.get('designation', ''),
            topic=request.POST.get('topic', ''),
            newsletter_consent=request.POST.get('newsletter') == 'on',
            status='pending',
            is_paid=False,
            payment_id=None,
            created_at=timezone.now()  # Use timezone-aware datetime
        )
        
        print(f"Booking created: {booking.booking_id}")
        
        # Handle optional document upload
        if 'documents' in request.FILES:
            booking.documents = request.FILES['documents']
            booking.save()
        
        print(f"=== BOOKING SUBMISSION COMPLETE ===")
        print(f"Booking ID: {booking.booking_id}")
        print(f"Status: {booking.status}")
        
        # Send initial booking confirmation email
        try:
            send_booking_confirmation_email(booking, details)
            print("Confirmation email sent")
        except Exception as e:
            print(f"Error sending booking emails: {e}")
        
        # Return success - redirect to admin page
        return JsonResponse({
            'success': True,
            'booking_id': str(booking.booking_id),
            'redirect_url': f'/booking/45-min/',
            'message': 'Booking created successfully. Admin will contact you for payment.'
        })
        
    except Exception as e:
        import traceback
        print(f"Error in booking submission: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': 'Server error: ' + str(e)})


# ══════════════════════════════════════════════════════════════════════════════
#                              EMAIL FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def send_booking_confirmation_email(booking, details):
    """Send comprehensive booking confirmation email to both user and admin."""
    try:
        # Send to user
        send_user_booking_email(booking, details)
        
        # Send to admin
        send_admin_booking_email(booking, details)
        
        logger.info(f"✓ Booking confirmation emails sent for booking {booking.booking_id}")
        return True
    except Exception as e:
        logger.error(f"✗ Error sending booking emails: {str(e)}")
        return False

def send_user_booking_email(booking, details):
    """Send booking email to user with manual payment instructions."""
    subject = f'Booking Confirmation - {booking.booking_id}'
    
    # Format date/time
    appointment_date = booking.appointment_date.strftime('%A, %B %d, %Y')
    appointment_time = booking.appointment_time.strftime('%I:%M %p')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body>
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>Booking Confirmed!</h2>
            <p>Dear {booking.name},</p>
            <p>Your consultation has been booked successfully.</p>
            
            <div style="background: #f9f9f9; padding: 15px; margin: 15px 0;">
                <h3>Booking Details</h3>
                <p><strong>Booking ID:</strong> {booking.booking_id}</p>
                <p><strong>Date:</strong> {appointment_date}</p>
                <p><strong>Time:</strong> {appointment_time}</p>
                <p><strong>Duration:</strong> {booking.get_duration_display()}</p>
                <p><strong>Mode:</strong> {booking.get_mode_display()}</p>
                <p><strong>Amount:</strong> ₹{booking.price}</p>
                <p><strong>Status:</strong> Pending Manual Payment Confirmation</p>
            </div>
            
            <p><strong>Payment Instructions:</strong></p>
            <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0;">
                <h4>📞 Manual Payment Process</h4>
                <p>Our team will contact you within 24 hours to:</p>
                <ol>
                    <li>Confirm your booking details</li>
                    <li>Provide payment instructions</li>
                    <li>Answer any questions you may have</li>
                </ol>
                <p><strong>Payment Methods Available:</strong> Bank Transfer, UPI, Cash</p>
            </div>
            
            <p><strong>Next Steps:</strong></p>
            <ol>
                <li>Our team will contact you for payment confirmation</li>
                <li>Meeting details will be sent once payment is confirmed</li>
                <li>Join 5 minutes before scheduled time</li>
            </ol>
            
            <p>View your booking: <a href="http://127.0.0.1:8000/booking/{booking.booking_id}/">Booking Details</a></p>
            
            <p>If you have any urgent questions, please contact us at kpregtech@gmail.com</p>
            
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
        to=[booking.email],
    )
    email.content_subtype = "html"
    email.send()


def send_admin_booking_email(booking, details):
    """Send booking notification to admin with manual payment note."""
    subject = f'📅 New Booking: {booking.name} - {booking.booking_id}'
    
    message = f"""
    NEW BOOKING RECEIVED - MANUAL PAYMENT REQUIRED
    
    Booking ID: {booking.booking_id}
    Time: {booking.created_at.strftime('%Y-%m-%d %H:%M:%S')}
    
    Client Information:
    Name: {booking.name}
    Email: {booking.email}
    Phone: {booking.phone}
    Company: {booking.company or 'N/A'}
    
    Appointment Details:
    Date: {booking.appointment_date}
    Time: {booking.appointment_time.strftime('%H:%M')}
    Duration: {booking.get_duration_display()}
    Mode: {booking.get_mode_display()}
    Amount: ₹{booking.price}
    
    Topic: {booking.topic}
    
    IMPORTANT: Payment is manual
    ----------------------------
    Status: Pending Manual Payment
    Payment Method: To be collected manually
    
    Action Required:
    1. Contact client to confirm booking: {booking.phone}
    2. Provide payment instructions
    3. Collect payment manually
    4. Update booking status in admin once payment received
    
    View booking: http://127.0.0.1:8000/admin/consultation/consultationbooking/
    """
    
    admin_email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL]
    )
    admin_email.send()

def send_admin_booking_notification(booking, details):
    """Send detailed booking notification to admin."""
    try:
        subject = f'📅 New Booking: {booking.name} - {booking.booking_id}'
        
        message = f"""
        NEW BOOKING RECEIVED
        
        Booking ID: {booking.booking_id}
        Created: {booking.created_at}
        
        CLIENT:
        Name: {booking.name}
        Email: {booking.email}
        Phone: {booking.phone}
        Company: {booking.company or 'N/A'}
        
        APPOINTMENT:
        Date: {booking.appointment_date}
        Time: {booking.appointment_time}
        Duration: {booking.get_duration_display()}
        Mode: {booking.get_mode_display()}
        
        PAYMENT:
        Amount: ₹{booking.price}
        Status: {'Paid' if booking.is_paid else 'Pending'}
        Method: {booking.payment.method if hasattr(booking, 'payment') else 'Not selected'}
        
        ADMIN ACTIONS:
        View: https://yourdomain.com/admin/bookings/
        Manage: https://yourdomain.com/admin/booking-management/
        """
        
        # Send to admin
        admin_email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL]
        )
        admin_email.send()
        
        return True
    except Exception as e:
        print(f"Error sending admin notification: {e}")
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
                    <p>We regret to inform you that your consultation booking with KP RegTech has been cancelled.</p>
                    
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
                        <a href="mailto:kpregtech@gmail.com" class="btn btn-contact">Contact Support</a>
                    </div>
                    
                    <h3>Next Steps:</h3>
                    <ul>
                        <li>You can book a new appointment through our <a href="https://anjali-bansal.com/services">services page</a></li>
                        <li>If you have any questions, please contact us at <a href="mailto:kpregtech@gmail.com">kpregtech@gmail.com</a></li>
                        <li>For refund inquiries, please email <a href="mailto:kpregtech@gmail.com">kpregtech@gmail.com</a></li>
                        <li>We apologize for any inconvenience caused and hope to assist you in the future</li>
                    </ul>
                    
                    <p>Best regards,<br>
                    <strong>KP RegTech</strong><br>
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                    <p>© {datetime.now().year} KP RegTech. All rights reserved.</p>
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
                <li>Payment should be done during the meeting through given phone number or upi id</li>
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
                       <a href="mailto:kpregtech@gmail.com">kpregtech@gmail.com</a></p>
                    
                    <p>Best regards,<br>
                    <strong>KP RegTech</strong><br>
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                    <p>© {datetime.now().year} KP RegTech. All rights reserved.</p>
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
    
    # Validate duration parameter
    try:
        duration_minutes = int(duration)
        if duration_minutes <= 0:
            duration_minutes = 45  # Default to 45 if invalid
    except (ValueError, TypeError):
        # If duration is not a number, use default
        duration_minutes = 45
    
    # Check if date is in the past
    if selected_date_obj < date.today():
        return JsonResponse({
            'date': selected_date,
            'duration': duration_minutes,
            'available_slots': []  # No slots for past dates
        })
    
    # ... rest of the function remains the same
    
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
    
    # Validate duration parameter
    try:
        duration_minutes = int(duration)
        if duration_minutes <= 0:
            duration_minutes = 45  # Default to 45 if invalid
    except (ValueError, TypeError):
        # If duration is not a number, use default
        duration_minutes = 45
    
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
                    # Use datetime.time class instead of time() function
                    from datetime import time as time_class
                    check_time = time_class(hour, minute)
                    
                    # Calculate if slot fits in working hours
                    duration_td = timedelta(minutes=duration_minutes)
                    start_dt = datetime.combine(current_date, check_time)
                    end_dt = start_dt + duration_td
                    
                    # Slot must end before 5 PM
                    if end_dt.time() <= time_class(17, 0):
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
        'duration': duration_minutes,
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
#                              PAYMENT VIEWS
# ══════════════════════════════════════════════════════════════════════════════

# def initiate_payment(request, booking_id):
#     """
#     Initiate payment for a booking.
#     """
#     booking = get_object_or_404(ConsultationBooking, booking_id=booking_id)
    
#     # Check if payment already exists
#     if hasattr(booking, 'payment') and booking.payment.is_successful():
#         messages.info(request, 'Payment already completed for this booking.')
#         return redirect('booking_detail', booking_id=booking_id)
    
#     # Initiate payment
#     payment_data = booking.initiate_payment()
    
#     if not payment_data:
#         messages.error(request, 'Error initiating payment. Please try again.')
#         return redirect('booking_detail', booking_id=booking_id)
    
#     context = {
#         'booking': booking,
#         'payment_data': payment_data,
#         'razorpay_key_id': settings.RAZORPAY_KEY_ID,
#     }
    
#     return render(request, 'payment/payment.html', context)

# def payment_success(request):
#     """
#     Handle successful payment.
#     """
#     payment_id = request.GET.get('payment_id')
#     order_id = request.GET.get('order_id')
#     signature = request.GET.get('signature')
    
#     try:
#         # Verify payment with Razorpay
#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
#         # Get payment details
#         payment = client.payment.fetch(payment_id)
        
#         # Get our payment record
#         payment_record = Payment.objects.get(razorpay_order_id=order_id)
        
#         # Verify signature
#         params_dict = {
#             'razorpay_order_id': order_id,
#             'razorpay_payment_id': payment_id,
#             'razorpay_signature': signature
#         }
        
#         try:
#             client.utility.verify_payment_signature(params_dict)
            
#             # Update payment record
#             payment_record.mark_as_completed(
#                 payment_id=payment_id,
#                 method=payment.get('method'),
#                 additional_info={
#                     'upi_id': payment.get('vpa'),
#                     'card_last4': payment.get('card', {}).get('last4'),
#                     'bank_name': payment.get('bank')
#                 }
#             )
            
#             # Send confirmation email
#             send_payment_confirmation_email(payment_record.booking)
            
#             messages.success(request, 'Payment completed successfully!')
#             return render(request, 'payment/success.html', {
#                 'booking': payment_record.booking,
#                 'payment': payment_record
#             })
            
#         except razorpay.errors.SignatureVerificationError:
#             payment_record.status = 'failed'
#             payment_record.error_description = 'Signature verification failed'
#             payment_record.save()
            
#             messages.error(request, 'Payment verification failed. Please contact support.')
#             return redirect('payment_failed')
            
#     except Exception as e:
#         logger.error(f"Error processing payment success: {str(e)}")
#         messages.error(request, 'Error processing payment. Please contact support.')
#         return redirect('payment_failed')

# def payment_failed(request):
#     """
#     Handle failed payment.
#     """
#     order_id = request.GET.get('order_id', '')
    
#     context = {
#         'order_id': order_id,
#     }
    
#     return render(request, 'payment/failed.html', context)

# @csrf_exempt
# def razorpay_webhook(request):
#     """
#     Handle Razorpay webhook for payment status updates.
#     """
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#     try:
#         webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
#         webhook_signature = request.headers.get('X-Razorpay-Signature', '')
        
#         # Verify webhook signature
#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
#         # Get webhook body
#         webhook_body = request.body.decode('utf-8')
        
#         # Verify signature
#         client.utility.verify_webhook_signature(webhook_body, webhook_signature, webhook_secret)
        
#         # Parse webhook data
#         webhook_data = json.loads(webhook_body)
#         event = webhook_data.get('event')
        
#         if event == 'payment.captured':
#             payment_data = webhook_data.get('payload', {}).get('payment', {}).get('entity', {})
            
#             # Update payment in database
#             payment_id = payment_data.get('id')
#             order_id = payment_data.get('order_id')
            
#             try:
#                 payment = Payment.objects.get(razorpay_order_id=order_id)
#                 payment.mark_as_completed(
#                     payment_id=payment_id,
#                     method=payment_data.get('method'),
#                     additional_info={
#                         'upi_id': payment_data.get('vpa'),
#                         'card_last4': payment_data.get('card', {}).get('last4'),
#                         'bank_name': payment_data.get('bank')
#                     }
#                 )
                
#                 logger.info(f"Payment {payment_id} marked as completed via webhook")
                
#             except Payment.DoesNotExist:
#                 logger.error(f"Payment with order_id {order_id} not found")
        
#         return JsonResponse({'status': 'success'})
        
#     except Exception as e:
#         logger.error(f"Error processing webhook: {str(e)}")
#         return JsonResponse({'error': str(e)}, status=400)

# def send_payment_confirmation_email(booking):
#     """
#     Send payment confirmation email to client.
#     """
#     try:
#         subject = f'Payment Confirmed - Booking {booking.booking_id}'
        
#         # Create HTML email content
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
#                 .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
#                 .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
#                 .content {{ padding: 20px; background-color: #f9f9f9; }}
#                 .details {{ background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
#                 .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>Payment Confirmed!</h1>
#                 </div>
#                 <div class="content">
#                     <p>Dear {booking.name},</p>
#                     <p>Thank you for your payment. Your consultation booking is now confirmed.</p>
                    
#                     <div class="details">
#                         <h3>Payment Details</h3>
#                         <p><strong>Booking ID:</strong> {booking.booking_id}</p>
#                         <p><strong>Amount Paid:</strong> ₹{booking.price}</p>
#                         <p><strong>Payment Status:</strong> Completed</p>
#                         <p><strong>Date:</strong> {timezone.now().strftime('%d %B, %Y %I:%M %p')}</p>
#                     </div>
                    
#                     <div class="details">
#                         <h3>Appointment Details</h3>
#                         <p><strong>Date:</strong> {booking.appointment_date.strftime('%A, %d %B, %Y')}</p>
#                         <p><strong>Time:</strong> {booking.appointment_time.strftime('%I:%M %p')}</p>
#                         <p><strong>Duration:</strong> {booking.get_duration_display()}</p>
#                         <p><strong>Mode:</strong> {booking.get_mode_display()}</p>
#                     </div>
                    
#                     <p><strong>Important:</strong> Meeting details will be sent to you 1 hour before the appointment.</p>
                    
#                     <p>If you have any questions, please contact us at <a href="mailto:kpregtech@gmail.com">kpregtech@gmail.com</a></p>
                    
#                     <p>Best regards,<br>
#                     <strong>KP RegTech</strong><br>
#                     </p>
#                 </div>
#                 <div class="footer">
#                     <p>This is an automated email. Please do not reply to this message.</p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
        
#         # Send email
#         email = EmailMessage(
#             subject=subject,
#             body=html_content,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[booking.email],
#         )
#         email.content_subtype = "html"
#         email.send()
        
#         logger.info(f"Payment confirmation email sent to {booking.email}")
        
#         return True
        
#     except Exception as e:
#         logger.error(f"Error sending payment confirmation email: {str(e)}")
#         return False


# ══════════════════════════════════════════════════════════════════════════════
#                              TEST PAYMENT VIEWS (NO RAZORPAY)
# ══════════════════════════════════════════════════════════════════════════════

# import random
# from .models import Payment
# # In views.py, update the initiate_payment function:
# def initiate_payment(request, booking_id):
#     """
#     Initiate payment for a booking (TEST MODE).
#     """
#     print(f"Initiating payment for booking: {booking_id}")
    
#     try:
#         booking = ConsultationBooking.objects.get(booking_id=booking_id)
#         print(f"Booking found: {booking_id}, Name: {booking.name}, Price: {booking.price}")
        
#         # Check if already paid
#         if booking.is_paid:
#             print(f"Booking already paid: {booking_id}")
#             messages.info(request, 'This booking is already paid.')
#             return redirect('booking_detail', booking_id=booking_id)
        
#         # Check if payment already exists
#         try:
#             payment = Payment.objects.get(booking=booking)
#             print(f"Existing payment found: {payment.payment_id}, Status: {payment.status}")
#         except Payment.DoesNotExist:
#             # Create new payment record
#             payment = Payment.objects.create(
#                 booking=booking,
#                 amount=booking.price,
#                 method='upi',  # Default
#                 status='pending'
#             )
#             print(f"New payment created: {payment.payment_id}")
        
#         context = {
#             'booking': booking,
#             'payment': payment,
#             'is_test_mode': True,
#         }
        
#         print(f"Rendering payment test page for booking: {booking_id}")
#         return render(request, 'payment/payment_test_fixed.html', context)
        
#     except ConsultationBooking.DoesNotExist:
#         print(f"Booking not found: {booking_id}")
#         messages.error(request, 'Booking not found.')
#         return redirect('/')
#     except Exception as e:
#         print(f"Error initiating payment: {e}")
#         messages.error(request, f'Error: {str(e)}')
#         return redirect('/')


# # In views.py, update process_test_payment:
# # In views.py, update process_test_payment function:


# def process_test_payment(request, payment_id):
#     """Process test payment (simulates payment gateway)."""
#     print(f"Processing test payment: {payment_id}")
    
#     try:
#         payment = Payment.objects.get(payment_id=payment_id)
#         booking = payment.booking
        
#         print(f"Payment found: {payment_id}, Status: {payment.status}, Booking: {booking.booking_id}")
        
#         # Prevent duplicate processing
#         if payment.status == 'success' and booking.is_paid:
#             messages.info(request, 'Payment already completed.')
#             return redirect('booking_detail', booking_id=booking.booking_id)
        
#         if request.method == 'POST':
#             payment_method = request.POST.get('payment_method', payment.method)
#             simulate_success = request.POST.get('simulate_success') == 'true'
#             cash_verified = request.POST.get('cash_verified') == 'true'
            
#             print(f"Processing: method={payment_method}, success={simulate_success}, cash_verified={cash_verified}")
            
#             if simulate_success:
#                 if payment_method == 'cash':
#                     if cash_verified:
#                         # Cash verified by admin
#                         if not payment.cash_payment_verified:
#                             payment.mark_as_paid(
#                                 verified_by=request.user if request.user.is_authenticated else None,
#                                 notes="Verified by admin"
#                             )
#                             print(f"Cash payment verified: {payment_id}")
#                             messages.success(request, 'Cash payment verified! Booking confirmed.')
#                         else:
#                             messages.info(request, 'Cash payment already verified.')
#                     else:
#                         # Cash payment recorded but not verified yet
#                         if payment.status != 'pending':
#                             payment.status = 'pending'
#                             payment.transaction_id = f"CASH-{int(time.time())}"
#                             payment.save()
                            
#                             # Update booking status but keep as pending
#                             booking.status = 'pending'
#                             booking.payment_id = payment.payment_id
#                             booking.is_paid = False
#                             booking.save()
                            
#                             print(f"Cash payment recorded (pending verification): {payment_id}")
#                             send_cash_payment_pending_email(payment)
                            
#                             messages.info(request, 'Cash payment recorded. Your booking will be confirmed after payment verification.')
#                 else:
#                     # Online payment
#                     if payment.status != 'success':
#                         payment.status = 'success'
#                         payment.completed_at = timezone.now()
#                         payment.transaction_id = f"TXN{int(time.time())}{random.randint(1000, 9999)}"
#                         payment.method = payment_method
#                         payment.save()
                        
#                         # Update booking
#                         booking.is_paid = True
#                         booking.payment_id = payment.payment_id
#                         booking.status = 'confirmed'
#                         booking.confirmed_at = timezone.now()
#                         booking.save()
                        
#                         print(f"Online payment marked as success: {payment_id}")
#                         payment.send_payment_confirmation()
                        
#                         messages.success(request, 'Payment successful! Booking confirmed.')
#                     else:
#                         messages.info(request, 'Payment already completed.')
                
#                 # Redirect to booking detail page after successful payment
#                 return redirect('booking_detail', booking_id=booking.booking_id)
                
#             else:
#                 # Simulate failed payment
#                 if payment.status != 'failed':
#                     payment.status = 'failed'
#                     payment.save()
#                     print(f"Payment marked as failed: {payment_id}")
                    
#                     send_payment_failed_email(payment)
#                     messages.error(request, 'Payment failed. Please try again.')
#                 else:
#                     messages.info(request, 'Payment already marked as failed.')
                
#                 return redirect('payment_failed_test')
        
#         # If not POST, redirect back to payment page
#         return redirect('initiate_payment', booking_id=booking.booking_id)
        
#     except Payment.DoesNotExist:
#         print(f"Payment not found: {payment_id}")
#         messages.error(request, 'Payment record not found.')
#         return redirect('payment_failed_test')
#     except Exception as e:
#         print(f"Error in process_test_payment: {e}")
#         messages.error(request, f'Error: {str(e)}')
#         return redirect('payment_failed_test')


# def send_payment_confirmation_email_test(payment):
#     """
#     Send test payment confirmation email to client.
#     """
#     try:
#         booking = payment.booking
#         subject = f'TEST MODE - Payment Confirmed - Booking {booking.booking_id}'
        
#         # Create HTML email content
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
#                 .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
#                 .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
#                 .content {{ padding: 20px; background-color: #f9f9f9; }}
#                 .details {{ background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
#                 .test-note {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
#                 .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>TEST MODE - Payment Confirmed!</h1>
#                 </div>
#                 <div class="content">
#                     <p>Dear {booking.name},</p>
                    
#                     <div class="test-note">
#                         <strong>⚠️ TEST MODE ⚠️</strong>
#                         <p>This is a test payment confirmation. No real money was charged.</p>
#                     </div>
                    
#                     <div class="details">
#                         <h3>Payment Details</h3>
#                         <p><strong>Payment ID:</strong> {payment.payment_id}</p>
#                         <p><strong>Transaction ID:</strong> {payment.transaction_id or 'N/A'}</p>
#                         <p><strong>Amount:</strong> ₹{payment.amount}</p>
#                         <p><strong>Method:</strong> {payment.get_method_display()}</p>
#                         <p><strong>Status:</strong> {payment.get_status_display()}</p>
#                         <p><strong>Date:</strong> {payment.completed_at.strftime('%d %B, %Y %I:%M %p') if payment.completed_at else 'N/A'}</p>
#                     </div>
                    
#                     <div class="details">
#                         <h3>Appointment Details</h3>
#                         <p><strong>Booking ID:</strong> {booking.booking_id}</p>
#                         <p><strong>Date:</strong> {booking.appointment_date.strftime('%A, %d %B, %Y')}</p>
#                         <p><strong>Time:</strong> {booking.appointment_time.strftime('%I:%M %p')}</p>
#                         <p><strong>Duration:</strong> {booking.get_duration_display()}</p>
#                         <p><strong>Mode:</strong> {booking.get_mode_display()}</p>
#                     </div>
                    
#                     <p><strong>Note:</strong> This was a test transaction. Your consultation is confirmed.</p>
                    
#                     <p>Best regards,<br>
#                     <strong>KP RegTech</strong><br>
#                     </p>
#                 </div>
#                 <div class="footer">
#                     <p>This is an automated email from test system. Please do not reply.</p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
        
#         # In a real app, use EmailMessage
#         print(f"TEST EMAIL: Payment confirmation would be sent to {booking.email}")
#         print(f"TEST EMAIL: Subject: {subject}")
        
#         return True
        
#     except Exception as e:
#         print(f"Error sending test payment email: {e}")
#         return False
# # In views.py, update the payment_success_test function:
# def payment_success_test(request, payment_id):
#     """
#     Show payment success page (TEST MODE).
#     """
#     print(f"Showing success page for payment: {payment_id}")
    
#     try:
#         # Get payment with related booking
#         payment = Payment.objects.select_related('booking').get(payment_id=payment_id)
#         booking = payment.booking
        
#         print(f"Success - Payment: {payment_id}, Booking: {booking.booking_id}, Status: {payment.status}")
        
#         context = {
#             'payment': payment,
#             'booking': booking,
#             'is_test_mode': True,
#         }
        
#         return render(request, 'payment/success_test.html', context)
        
#     except Payment.DoesNotExist:
#         print(f"Payment not found for success page: {payment_id}")
#         messages.error(request, 'Payment not found.')
#         return redirect('payment_failed_test')
#     except Exception as e:
#         print(f"Error loading success page: {e}")
#         messages.error(request, f'Error: {str(e)}')
#         return redirect('payment_failed_test')

# # In views.py, update the payment_failed_test function:
# def payment_failed_test(request):
#     """
#     Show payment failed page (TEST MODE).
#     """
#     print("Showing payment failed page")
    
#     context = {
#         'is_test_mode': True,
#     }
    
#     return render(request, 'payment/failed_test.html', context)


# def booking_detail(request, booking_id):
#     """
#     View booking details and payment status.
#     """
#     booking = get_object_or_404(ConsultationBooking, booking_id=booking_id)
    
#     context = {
#         'booking': booking,
#         'has_payment': hasattr(booking, 'payment'),
#     }
    
#     return render(request, 'booking/detail.html', context)
# # # ══════════════════════════════════════════════════════════════════════════════
# # #                                  END OF VIEWS
# # # ══════════════════════════════════════════════════════════════════════════════

# def test_booking_flow(request):
#     """Test endpoint to check booking flow."""
#     return JsonResponse({
#         'status': 'test_ok',
#         'message': 'Booking endpoint is reachable',
#         'expected_redirect': '/booking/{booking_id}/payment-test/'
#     })

# # In views.py, add this view:
# def debug_payment_state(request):
#     """
#     Debug view to check payment and booking state.
#     """
#     from django.db import connection
    
#     html = "<h1>Payment Debug Information</h1>"
    
#     # Check all payments
#     html += "<h2>All Payments</h2>"
#     payments = Payment.objects.all().select_related('booking')
#     html += f"<p>Total payments: {payments.count()}</p>"
#     html += "<table border='1'><tr><th>Payment ID</th><th>Booking ID</th><th>Amount</th><th>Status</th><th>Method</th><th>Created</th></tr>"
#     for p in payments:
#         html += f"<tr><td>{p.payment_id}</td><td>{p.booking.booking_id if p.booking else 'N/A'}</td><td>{p.amount}</td><td>{p.status}</td><td>{p.method}</td><td>{p.created_at}</td></tr>"
#     html += "</table>"
    
#     # Check all bookings
#     html += "<h2>All Bookings</h2>"
#     bookings = ConsultationBooking.objects.all()
#     html += f"<p>Total bookings: {bookings.count()}</p>"
#     html += "<table border='1'><tr><th>Booking ID</th><th>Name</th><th>Email</th><th>Amount</th><th>Paid</th><th>Status</th><th>Appointment Date</th></tr>"
#     for b in bookings:
#         html += f"<tr><td>{b.booking_id}</td><td>{b.name}</td><td>{b.email}</td><td>{b.price}</td><td>{b.is_paid}</td><td>{b.status}</td><td>{b.appointment_date}</td></tr>"
#     html += "</table>"
    
#     # Check database tables
#     html += "<h2>Database Tables</h2>"
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
#         tables = cursor.fetchall()
#         html += "<ul>"
#         for table in tables:
#             html += f"<li>{table[0]}</li>"
#         html += "</ul>"
    
#     return HttpResponse(html)


# # In views.py, add:
# def test_payment_flow(request):
#     """
#     Test endpoint to create a test booking and payment.
#     """
#     try:
#         # Create a test booking
#         from datetime import datetime, timedelta
#         from django.utils import timezone
        
#         booking = ConsultationBooking.objects.create(
#             duration='30-min',
#             price=1000,
#             appointment_date=timezone.now().date() + timedelta(days=1),
#             appointment_time=(datetime.now() + timedelta(hours=1)).time(),
#             mode='video',
#             name='Test User',
#             email='test@example.com',
#             phone='9876543210',
#             topic='Test consultation',
#             status='pending'
#         )
        
#         # Create a test payment
#         payment = Payment.objects.create(
#             booking=booking,
#             amount=booking.price,
#             method='upi',
#             status='pending'
#         )
        
#         return JsonResponse({
#             'status': 'success',
#             'booking_id': str(booking.booking_id),
#             'payment_id': payment.payment_id,
#             'payment_url': f'/booking/{booking.booking_id}/payment-test/',
#             'process_url': f'/payment/test/process/{payment.payment_id}/',
#             'success_url': f'/payment/test/success/{payment.payment_id}/'
#         })
        
#     except Exception as e:
#         return JsonResponse({
#             'status': 'error',
#             'error': str(e)
#         })
    
# # In views.py, add:
# from django.contrib.admin.views.decorators import staff_member_required

# @staff_member_required
# def admin_verify_cash_payment(request, payment_id):
#     """Admin view to verify cash payments."""
#     try:
#         payment = Payment.objects.get(payment_id=payment_id, method='cash')
        
#         if request.method == 'POST':
#             notes = request.POST.get('notes', '')
            
#             # Verify the cash payment
#             payment.mark_as_paid(verified_by=request.user, notes=notes)
            
#             # Update booking status
#             payment.booking.is_paid = True
#             payment.booking.status = 'confirmed'
#             payment.booking.save()
            
#             messages.success(request, f'Cash payment verified for {payment.booking.name}')
#             return redirect('admin_booking_management')
        
#         context = {
#             'payment': payment,
#             'booking': payment.booking,
#         }
        
#         return render(request, 'admin/verify_cash_payment.html', context)
        
#     except Payment.DoesNotExist:
#         messages.error(request, 'Payment not found.')
#         return redirect('admin_booking_management')


# # Add these functions in views.py:

# def send_cash_payment_pending_email(payment):
#     """
#     Send email for cash payment pending verification.
#     """
#     try:
#         booking = payment.booking
#         subject = f'Cash Payment Recorded - Booking {booking.booking_id}'
        
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
#                 .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
#                 .header {{ background-color: #ffc107; color: #856404; padding: 20px; text-align: center; }}
#                 .content {{ padding: 20px; background-color: #f9f9f9; }}
#                 .details {{ background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
#                 .action-buttons {{ text-align: center; margin: 20px 0; }}
#                 .btn {{ display: inline-block; padding: 10px 20px; margin: 5px; text-decoration: none; border-radius: 5px; }}
#                 .btn-online {{ background-color: #28a745; color: white; }}
#                 .btn-contact {{ background-color: #007bff; color: white; }}
#                 .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>Cash Payment Recorded</h1>
#                 </div>
#                 <div class="content">
#                     <p>Dear {booking.name},</p>
#                     <p>Thank you for choosing cash/offline payment for your consultation booking.</p>
                    
#                     <div class="details">
#                         <h3>Booking Details</h3>
#                         <p><strong>Booking ID:</strong> {booking.booking_id}</p>
#                         <p><strong>Amount:</strong> ₹{booking.price}</p>
#                         <p><strong>Payment Method:</strong> Cash/Offline</p>
#                         <p><strong>Payment Status:</strong> Pending Verification</p>
#                         <p><strong>Date:</strong> {booking.appointment_date.strftime('%A, %d %B, %Y')}</p>
#                         <p><strong>Time:</strong> {booking.appointment_time.strftime('%I:%M %p')}</p>
#                     </div>
                    
#                     <p><strong>Important:</strong> Your booking is confirmed, but you need to complete the payment before your appointment.</p>
                    
#                     <div class="action-buttons">
#                         <a href="https://anjali-bansal.com/booking/{booking.booking_id}/payment-test/" class="btn btn-online">
#                             Switch to Online Payment
#                         </a>
#                         <a href="mailto:kpregtech@gmail.com" class="btn btn-contact">
#                             Contact for Payment Details
#                         </a>
#                     </div>
                    
#                     <h4>Payment Options:</h4>
#                     <ul>
#                         <li><strong>Office Payment:</strong> Visit our office with Booking ID</li>
#                         <li><strong>Bank Transfer:</strong> Transfer to our bank account</li>
#                         <li><strong>Switch to Online:</strong> Use the button above to pay online</li>
#                     </ul>
                    
#                     <p>Once payment is received, you'll receive a confirmation email.</p>
                    
#                     <p>Best regards,<br>
#                     <strong>KP RegTech</strong><br>
#                     </p>
#                 </div>
#                 <div class="footer">
#                     <p>This is an automated email. Please do not reply to this message.</p>
#                     <p>© {timezone.now().year} KP RegTech. All rights reserved.</p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
        
#         # In a real app, use EmailMessage
#         print(f"CASH PAYMENT EMAIL: Sent to {booking.email}")
#         print(f"CASH PAYMENT EMAIL: Subject: {subject}")
        
#         return True
        
#     except Exception as e:
#         print(f"Error sending cash payment email: {e}")
#         return False

# def send_payment_failed_email(payment):
#     """
#     Send email for failed payment.
#     """
#     try:
#         booking = payment.booking
#         subject = f'Payment Failed - Booking {booking.booking_id}'
        
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
#                 .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
#                 .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
#                 .content {{ padding: 20px; background-color: #f9f9f9; }}
#                 .details {{ background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
#                 .action-buttons {{ text-align: center; margin: 20px 0; }}
#                 .btn {{ display: inline-block; padding: 10px 20px; margin: 5px; text-decoration: none; border-radius: 5px; }}
#                 .btn-retry {{ background-color: #28a745; color: white; }}
#                 .btn-cash {{ background-color: #007bff; color: white; }}
#                 .btn-contact {{ background-color: #6c757d; color: white; }}
#                 .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>Payment Failed</h1>
#                 </div>
#                 <div class="content">
#                     <p>Dear {booking.name},</p>
#                     <p>We were unable to process your payment for the consultation booking.</p>
                    
#                     <div class="details">
#                         <h3>Booking Details</h3>
#                         <p><strong>Booking ID:</strong> {booking.booking_id}</p>
#                         <p><strong>Amount:</strong> ₹{booking.price}</p>
#                         <p><strong>Payment Method:</strong> {payment.get_method_display()}</p>
#                         <p><strong>Payment Status:</strong> Failed</p>
#                     </div>
                    
#                     <div class="action-buttons">
#                         <a href="https://anjali-bansal.com/booking/{booking.booking_id}/payment-test/" class="btn btn-retry">
#                             Retry Payment
#                         </a>
#                         <a href="https://anjali-bansal.com/booking/{booking.booking_id}/payment-test/?method=cash" class="btn btn-cash">
#                             Switch to Cash Payment
#                         </a>
#                         <a href="mailto:kpregtech@gmail.com" class="btn btn-contact">
#                             Contact Support
#                         </a>
#                     </div>
                    
#                     <p><strong>Your booking is still reserved for:</strong></p>
#                     <ul>
#                         <li><strong>Date:</strong> {booking.appointment_date.strftime('%A, %d %B, %Y')}</li>
#                         <li><strong>Time:</strong> {booking.appointment_time.strftime('%I:%M %p')}</li>
#                         <li><strong>Duration:</strong> {booking.get_duration_display()}</li>
#                     </ul>
                    
#                     <p>Please complete the payment to confirm your booking.</p>
                    
#                     <p>Best regards,<br>
#                     <strong>KP RegTech</strong><br>
#                     </p>
#                 </div>
#                 <div class="footer">
#                     <p>This is an automated email. Please do not reply to this message.</p>
#                     <p>© {timezone.now().year} KP RegTech. All rights reserved.</p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
        
#         # In a real app, use EmailMessage
#         print(f"FAILED PAYMENT EMAIL: Sent to {booking.email}")
#         print(f"FAILED PAYMENT EMAIL: Subject: {subject}")
        
#         return True
        
#     except Exception as e:
#         print(f"Error sending failed payment email: {e}")
#         return False
    
# @staff_member_required
# def admin_process_refund(request, booking_id):
#     """Admin view to process refunds."""
#     booking = get_object_or_404(ConsultationBooking, booking_id=booking_id)
    
#     if request.method == 'POST':
#         reason = request.POST.get('reason', '')
#         refund_amount = request.POST.get('refund_amount', booking.price)
        
#         # Create refund record
#         refund = razorpay.Refund.objects.create(
#             booking=booking,
#             payment=booking.payment,
#             amount=refund_amount,
#             reason=reason,
#             status='requested'
#         )
        
#         # Send refund request email to admin
#         send_refund_request_email(refund)
        
#         messages.success(request, f'Refund request created for booking {booking_id}')
#         return redirect('admin_booking_management')
    
#     context = {
#         'booking': booking,
#     }
#     return render(request, 'admin/process_refund.html', context)

# def send_refund_request_email(refund):
#     """Send refund request email."""
#     try:
#         subject = f'Refund Request - Booking {refund.booking.booking_id}'
        
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <body>
#             <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
#                 <h2>Refund Request Submitted</h2>
#                 <p>Dear {refund.booking.name},</p>
#                 <p>Your refund request has been submitted successfully.</p>
                
#                 <div style="background: #f9f9f9; padding: 15px; margin: 15px 0;">
#                     <h3>Refund Details</h3>
#                     <p><strong>Refund ID:</strong> {refund.refund_id}</p>
#                     <p><strong>Booking ID:</strong> {refund.booking.booking_id}</p>
#                     <p><strong>Amount:</strong> ₹{refund.amount}</p>
#                     <p><strong>Reason:</strong> {refund.reason}</p>
#                     <p><strong>Status:</strong> Pending Approval</p>
#                 </div>
                
#                 <p>We will review your request and get back to you within 3-5 business days.</p>
                
#                 <p>Best regards,<br>
#                 <strong>KP RegTech</strong></p>
#             </div>
#         </body>
#         </html>
#         """
        
#         email = EmailMessage(
#             subject=subject,
#             body=html_content,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[refund.booking.email],
#         )
#         email.content_subtype = "html"
#         email.send()
        
#         logger.info(f"Refund request email sent to {refund.booking.email}")
#         return True
#     except Exception as e:
#         logger.error(f"Error sending refund email: {str(e)}")
#         return False
    
# from django.http import HttpResponse
# import csv


# def download_booking_details(request, booking_id):
#     """Download booking details as PDF - FIXED VERSION"""
#     booking = get_object_or_404(ConsultationBooking, booking_id=booking_id)
    
#     # Check permission
#     if not request.user.is_staff and booking.email != request.user.email:
#         messages.error(request, 'You are not authorized to download these details.')
#         return redirect('booking_detail', booking_id=booking_id)
    
#     format_type = request.GET.get('format', 'pdf')
    
#     try:
#         if format_type == 'csv':
#             return download_booking_csv(booking)
#         else:
#             return download_booking_pdf(booking)
#     except Exception as e:
#         print(f"Error downloading booking: {e}")
#         messages.error(request, f'Error generating download: {str(e)}')
#         return redirect('booking_detail', booking_id=booking_id)

# def download_booking_pdf(booking):
#     """Download booking details as PDF - FIXED VERSION"""
#     from reportlab.lib import colors
#     from reportlab.lib.pagesizes import letter
#     from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
#     from reportlab.lib.styles import getSampleStyleSheet
#     from io import BytesIO
    
#     buffer = BytesIO()
    
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     styles = getSampleStyleSheet()
#     story = []
    
#     # Title
#     story.append(Paragraph("Booking Confirmation - KP RegTech", styles['Title']))
#     story.append(Spacer(1, 12))
    
#     # Get payment if exists
#     try:
#         payment = Payment.objects.get(booking=booking)
#         has_payment = True
#     except Payment.DoesNotExist:
#         has_payment = False
#         payment = None
    
#     # Booking Information
#     story.append(Paragraph(f"Booking ID: {booking.booking_id}", styles['Normal']))
#     story.append(Paragraph(f"Date Created: {booking.created_at.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
#     story.append(Spacer(1, 12))
    
#     # Client Information
#     client_data = [
#         ['Client Information', ''],
#         ['Name:', booking.name],
#         ['Email:', booking.email],
#         ['Phone:', booking.phone],
#         ['Company:', booking.company or 'N/A'],
#         ['Designation:', booking.designation or 'N/A']
#     ]
    
#     client_table = Table(client_data, colWidths=[150, 300])
#     client_table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 12),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('PADDING', (0, 0), (-1, -1), 6),
#     ]))
    
#     story.append(client_table)
#     story.append(Spacer(1, 12))
    
#     # Appointment Details
#     appointment_data = [
#         ['Appointment Details', ''],
#         ['Date:', booking.appointment_date.strftime('%A, %d %B, %Y')],
#         ['Time:', booking.appointment_time.strftime('%I:%M %p')],
#         ['Duration:', booking.get_duration_display()],
#         ['Mode:', booking.get_mode_display()],
#         ['Amount:', f'₹{booking.price}'],
#         ['Payment Status:', 'Paid' if booking.is_paid else 'Pending']
#     ]
    
#     if has_payment and payment:
#         appointment_data.append(['Payment Method:', payment.get_method_display()])
#         appointment_data.append(['Payment ID:', payment.payment_id])
#         if payment.method == 'cash':
#             appointment_data.append(['Cash Verified:', 'Yes' if payment.cash_payment_verified else 'No'])
    
#     appointment_table = Table(appointment_data, colWidths=[150, 300])
#     appointment_table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 12),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('PADDING', (0, 0), (-1, -1), 6),
#     ]))
    
#     story.append(appointment_table)
#     story.append(Spacer(1, 12))
    
#     # Consultation Topic
#     if booking.topic:
#         story.append(Paragraph("Consultation Topic:", styles['Heading2']))
#         story.append(Paragraph(booking.topic, styles['Normal']))
#         story.append(Spacer(1, 12))
    
#     # Footer
#     story.append(Paragraph("KP RegTech - ", styles['Normal']))
#     story.append(Paragraph("Email: kpregtech@gmail.com", styles['Normal']))
#     story.append(Paragraph(f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    
#     doc.build(story)
    
#     buffer.seek(0)
    
#     response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="booking_{booking.booking_id}.pdf"'
    
#     return response

# def download_booking_csv(booking):
#     """Download booking details as CSV."""
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="booking_{booking.booking_id}.csv"'
    
#     writer = csv.writer(response)
#     writer.writerow(['KP RegTech - Booking Confirmation'])
#     writer.writerow([])
#     writer.writerow(['Client Information'])
#     writer.writerow(['Name', booking.name])
#     writer.writerow(['Email', booking.email])
#     writer.writerow(['Phone', booking.phone])
#     writer.writerow(['Company', booking.company or 'N/A'])
#     writer.writerow(['Designation', booking.designation or 'N/A'])
#     writer.writerow([])
#     writer.writerow(['Appointment Details'])
#     writer.writerow(['Booking ID', booking.booking_id])
#     writer.writerow(['Date', booking.appointment_date.strftime('%Y-%m-%d')])
#     writer.writerow(['Time', booking.appointment_time.strftime('%H:%M')])
#     writer.writerow(['Duration', booking.get_duration_display()])
#     writer.writerow(['Mode', booking.get_mode_display()])
#     writer.writerow(['Amount', f'₹{booking.price}'])
#     writer.writerow(['Payment Status', 'Paid' if booking.is_paid else 'Pending'])
    
#     if hasattr(booking, 'payment'):
#         writer.writerow(['Payment Method', booking.payment.get_method_display()])
#         writer.writerow(['Payment ID', booking.payment.payment_id])
    
#     writer.writerow([])
#     writer.writerow(['Consultation Topic'])
#     writer.writerow([booking.topic])
#     writer.writerow([])
#     writer.writerow(['Generated on', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
    
#     return response

# # Django view example
# from django.http import JsonResponse
# import traceback

# def submit_booking(request):
#     try:
#         if request.method == 'POST':
#             # Process your form data
#             # ...
            
#             if success:
#                 return JsonResponse({
#                     'success': True,
#                     'booking_id': booking.id,
#                     'message': 'Booking confirmed successfully'
#                 })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Specific error message here'
#                 }, status=400)
                
#     except Exception as e:
#         # Log the error for debugging
#         print(traceback.format_exc())
#         return JsonResponse({
#             'success': False,
#             'error': 'An internal server error occurred'
#         }, status=500)
    
# def test_json_response(request):
#     """Simple test endpoint to verify JSON responses work."""
#     return JsonResponse({
#         'success': True,
#         'message': 'JSON response is working',
#         'timestamp': timezone.now().isoformat()
#     })

# # In views.py
# from django.core.mail import send_mail
# from django.http import JsonResponse

# def test_email_send(request):
#     """Test email sending"""
#     try:
#         print("sending email")
#         send_mail(
#             subject='Test Email from Django',
#             message='This is a test email from your Django application.',
#             from_email='KP RegTech <jangratushar348@gmail.com>',
#             recipient_list=['jangratushar348@gmail.com'],
#             fail_silently=False,
#         )
#         print("done")
#         return JsonResponse({'success': True, 'message': 'Test email sent!'})
        
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})


# from django.core.mail import send_mail
# from django.http import JsonResponse

# def test_email_send(request):
#     """Test email sending"""
#     try:
#         send_mail(
#             subject='Test Email from Django',
#             message='This is a test email from your Django application.',
#             from_email='KP RegTech <jangratushar348@gmail.com>',
#             recipient_list=['jangratushar348@gmail.com'],
#             fail_silently=False,
#         )
#         return JsonResponse({'success': True, 'message': 'Test email sent!'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})