# views.py - Complete version with all status notifications
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.db.models.functions import Lower, Trim
from django.db.models import Avg, Count
from django.template.loader import render_to_string
from datetime import datetime, timedelta, date
from .models import BlogPost, Testimonial, TestimonialSubmission, ConsultationBooking, AvailableSlot, BookedSlot
from .forms import TestimonialSubmissionForm
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)

# ============ EXISTING VIEWS ============ 
def index(request):
    # Get latest 3 blog posts for homepage
    latest_blogs = BlogPost.objects.filter(is_published=True)[:3]
    
    # Get active testimonials for homepage carousel
    testimonials = Testimonial.objects.filter(is_active=True, is_featured=True)[:4]
    
    context = {
        'latest_blogs': latest_blogs,
        'testimonials': testimonials,
    }
    return render(request, "index.html", context)

def about(request):
    return render(request, "about.html")

def our_expertise(request):
    return render(request, "our_expertise.html")

def contact(request):
    return render(request, "contact.html")

def blogs(request):
    all_blogs = BlogPost.objects.filter(is_published=True)

    category_filter = request.GET.get('category')

    # ✅ EXACT MATCH (choices are exact)
    if category_filter:
        all_blogs = all_blogs.filter(category=category_filter)

    # ✅ DISTINCT CATEGORIES (NO NORMALIZATION)
    categories = (
        BlogPost.objects
        .filter(is_published=True)
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )

    sort_by = request.GET.get('sort', 'latest')

    if sort_by == 'oldest':
        all_blogs = all_blogs.order_by('date_published')
    elif sort_by == 'popular':
        all_blogs = all_blogs.order_by('-read_time')
    else:
        all_blogs = all_blogs.order_by('-date_published')

    # ✅ PAGINATION — 3 POSTS PER PAGE
    paginator = Paginator(all_blogs, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "blogs.html", {
        'blogs': page_obj,
        'categories': categories,
        'current_category': category_filter,
        'current_sort': sort_by,
        'page_obj': page_obj,
    })

def blog_detail(request, slug):
    # Get single blog post
    blog = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Get related posts (same category)
    related_posts = BlogPost.objects.filter(
        category=blog.category, 
        is_published=True
    ).exclude(id=blog.id)[:3]
    
    context = {
        'blog': blog,
        'related_posts': related_posts,
    }
    return render(request, "blog_detail.html", context)

def testimonials(request):
    # Get all active testimonials
    all_testimonials = Testimonial.objects.filter(is_active=True)
    
    # Get featured testimonials for slider
    featured_testimonials = Testimonial.objects.filter(
        is_active=True, 
        is_featured=True
    )
    
    # Get unique industries for tabs
    industries = Testimonial.objects.filter(is_active=True).values_list(
        'industry', flat=True
    ).distinct()
    
    # Group testimonials by industry for the tabs
    testimonials_by_industry = {}
    for testimonial in all_testimonials:
        industry = testimonial.industry
        if industry not in testimonials_by_industry:
            testimonials_by_industry[industry] = []
        testimonials_by_industry[industry].append(testimonial)
    
    # Also create a flat list of testimonials for each industry
    # to make template access easier
    industry_testimonials = {}
    for industry in industries:
        industry_testimonials[industry] = Testimonial.objects.filter(
            industry=industry, 
            is_active=True
        )
    
    # Statistics for stats section
    stats = {
        'total_clients': Testimonial.objects.filter(is_active=True).count(),
        'avg_rating': round(Testimonial.objects.filter(is_active=True).aggregate(
            Avg('rating')
        )['rating__avg'] or 0, 1),
        'industries_served': len(industries),
    }
    
    video_testimonials = Testimonial.objects.filter(
        is_active=True,
        video_url__isnull=False
    ).exclude(video_url="")
    
    # Check if user is admin to show pending submissions
    pending_submissions = None
    if request.user.is_staff:
        pending_submissions = TestimonialSubmission.objects.filter(
            status='pending'
        ).count()
    
    context = {
        'all_testimonials': all_testimonials,
        'featured_testimonials': featured_testimonials,
        'testimonials_by_industry': testimonials_by_industry,  # Dictionary
        'industry_testimonials': industry_testimonials,  # QuerySet per industry
        'industries': industries,
        'stats': stats,
        'video_testimonials': video_testimonials,
        'pending_submissions': pending_submissions,
    }
    
    return render(request, "testimonials.html", context)

def services(request):
    return render(request,'services.html')

def privacy_policy(request):
    return render(request, 'privacy-policy.html')

def terms_and_conditions(request):
    return render(request, 'terms and conditions.html')

def disclaimer(request):
    return render(request, 'disclaimer.html')

def refund_policy(request):
    return render(request, 'refund-policy.html')

def submit_testimonial(request):
    if request.method == 'POST':
        form = TestimonialSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.status = 'pending'
            submission.save()
            
            # Send confirmation email to user
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
                    fail_silently=True,
                )
            except:
                pass  # Email sending is optional
            
            # Send notification to admin
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
            
            messages.success(request, 'Thank you! Your testimonial has been submitted for review.')
            return redirect('thank_you_testimonial')
    else:
        form = TestimonialSubmissionForm()
    
    # Get industries for the form
    industries = TestimonialSubmission.INDUSTRY_CHOICES
    
    context = {
        'form': form,
        'industries': industries,
    }
    
    # Use the correct template name - just 'submit_testimonial.html'
    return render(request, 'testimonials/submit_testimonial.html', context)

def thank_you_testimonial(request):
    return render(request, 'testimonials/thank_you.html', {})

@staff_member_required
def approve_testimonials(request):
    submissions = TestimonialSubmission.objects.filter(status='pending')
    
    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        submission = get_object_or_404(TestimonialSubmission, id=submission_id)
        
        if action == 'approve':
            # Create a Testimonial from submission
            testimonial = Testimonial.objects.create(
                client_name=submission.full_name,
                company=submission.company_name,
                position=submission.position,
                content=submission.testimonial_text,
                industry=submission.industry,
                rating=submission.rating,
                services=submission.services_used,
                is_active=True,
            )
            
            # Copy profile picture if exists
            if submission.profile_picture:
                testimonial.client_image.save(
                    submission.profile_picture.name,
                    submission.profile_picture
                )
            
            submission.status = 'approved'
            submission.approved_testimonial = testimonial
            submission.approved_date = timezone.now()
            submission.admin_notes = notes
            submission.is_public = True
            submission.save()
            
            # Send approval email
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
            
            messages.success(request, f'Testimonial from {submission.full_name} approved and published.')
            
        elif action == 'reject':
            submission.status = 'rejected'
            submission.admin_notes = notes
            submission.save()
            
            # Send rejection email
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
            
            messages.warning(request, f'Testimonial from {submission.full_name} rejected.')
    
    context = {
        'submissions': submissions,
    }
    
    return render(request, 'admin/approve_testimonials.html', context)

def debug_testimonials(request):
    testimonials = Testimonial.objects.all()
    submissions = TestimonialSubmission.objects.all()
    
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
    
    return HttpResponse(html)

# ============ BOOKING VIEWS ============
def booking(request, duration):
    # Get query parameters
    plan = request.GET.get('plan', '')
    original_duration = request.GET.get('duration', '')
    price = request.GET.get('price', '')
    
    # Map durations to display names and details
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
    
    # Get details for the requested duration
    details = duration_details.get(duration, duration_details['45-min'])
    
    if request.method == 'POST':
        return handle_booking_submission(request, duration, details)
    
    context = {
        'duration': duration,
        'title': details['title'],
        'price': details['price'],
        'price_amount': details['price_amount'],
        'duration_minutes': details['duration_minutes'],
        'features': details['features'],
        'referral': request.GET.get('referral', 'service_list_widget'),
        'plan_name': plan,
        'original_duration': original_duration
    }
    
    return render(request, 'booking.html', context)

def handle_booking_submission(request, duration, details):
    try:
        # Parse the appointment datetime
        appointment_datetime = request.POST.get('appointment_datetime')
        if not appointment_datetime:
            return JsonResponse({'success': False, 'error': 'No appointment time selected'})
        
        dt = datetime.fromisoformat(appointment_datetime)
        duration_minutes = int(duration.replace('-min', ''))
        
        # Check if date/time is in the past
        now = datetime.now()
        if dt < now:
            return JsonResponse({
                'success': False, 
                'error': 'Cannot book appointments in the past. Please select a future date and time.'
            })
        
        # Check if time is available (with 15 min buffer between appointments)
        if not is_time_available(dt.date(), dt.time(), duration_minutes):
            return JsonResponse({
                'success': False, 
                'error': 'This time slot is no longer available or overlaps with an existing booking. Please select another time.'
            })
        
        # Create booking
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
            status='confirmed'
        )
        
        # Handle file upload
        if 'documents' in request.FILES:
            booking.documents = request.FILES['documents']
            booking.save()
        
        # Log email attempt details
        logger.info(f"Attempting to send emails:")
        logger.info(f"  - To client: {booking.email}")
        logger.info(f"  - From: {settings.DEFAULT_FROM_EMAIL}")
        logger.info(f"  - EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        
        # Send emails
        client_email_sent = send_booking_confirmation_email(booking, details)
        admin_email_sent = send_admin_notification_email(booking, details)
        
        logger.info(f"Booking {booking.booking_id} created. Client email: {client_email_sent}, Admin email: {admin_email_sent}")
        
        return JsonResponse({
            'success': True,
            'booking_id': str(booking.booking_id),
            'client_email': booking.email,
            'admin_email': settings.ADMIN_EMAIL,
            'message': 'Booking confirmed successfully! Check your email for details.'
        })
        
    except Exception as e:
        logger.error(f"Error in booking submission: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

def send_booking_confirmation_email(booking, details):
    """Send confirmation email to client"""
    try:
        subject = f'Consultation Booking Confirmation - {booking.booking_id}'
        
        # Format date and time nicely
        appointment_date = booking.appointment_date.strftime('%A, %B %d, %Y')
        appointment_time = booking.appointment_time.strftime('%I:%M %p')
        
        # Calculate end time
        duration_minutes = int(booking.duration.replace('-min', ''))
        start_dt = datetime.combine(booking.appointment_date, booking.appointment_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        end_time = end_dt.strftime('%I:%M %p')
        
        # Create HTML email
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
        
        # Create plain text version
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
        
        # Send email to client
        email_to_client = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email],
        )
        email_to_client.content_subtype = "html"
        email_to_client.send()
        
        logger.info(f"✓ Confirmation email sent to {booking.email} for booking {booking.booking_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error sending confirmation email for booking {booking.booking_id}: {str(e)}")
        # Don't fail the booking if email fails
        return False

def send_admin_notification_email(booking, details):
    """Send notification email to admin"""
    try:
        subject = f'📅 New Booking: {booking.name} - {booking.appointment_date}'
        
        # Calculate end time
        duration_minutes = int(booking.duration.replace('-min', ''))
        start_dt = datetime.combine(booking.appointment_date, booking.appointment_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
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
    """Send cancellation email to client"""
    try:
        subject = f'Consultation Booking Cancelled - {booking.booking_id}'
        
        # Format date and time nicely
        appointment_date = booking.appointment_date.strftime('%A, %B %d, %Y')
        appointment_time = booking.appointment_time.strftime('%I:%M %p')
        
        # Calculate end time
        duration_minutes = int(booking.duration.replace('-min', ''))
        start_dt = datetime.combine(booking.appointment_date, booking.appointment_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        end_time = end_dt.strftime('%I:%M %p')
        
        # Use provided reason or default
        cancellation_reason = reason or booking.cancellation_reason or "due to unforeseen circumstances"
        
        # Create HTML email
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
        
        # Create plain text version
        plain_text = f"""Booking Cancelled
====================

Dear {booking.name},

We regret to inform you that your consultation booking with Anjali Bansal & Associates has been cancelled.

CANCELLED APPOINTMENT DETAILS:
Booking ID: {booking.booking_id}
Original Date: {appointment_date}
Original Time: {appointment_time} - {end_time} ({duration_minutes} minutes)
Duration: {booking.get_duration_display()}
Mode: {booking.get_mode_display()}
Amount: ₹{booking.price}

CANCELLATION REASON:
{cancellation_reason}

NEXT STEPS:
- You can book a new appointment through our services page: https://anjali-bansal.com/services
- If you have any questions, please contact us at: contact@anjali-bansal.com
- For refund inquiries, please email: billing@anjali-bansal.com

We apologize for any inconvenience caused and hope to assist you in the future.

Best regards,
Anjali Bansal & Associates
Company Secretaries
"""
        
        # Send email to client
        email_to_client = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email],
        )
        email_to_client.content_subtype = "html"
        email_to_client.send()
        
        logger.info(f"✓ Cancellation email sent to {booking.email} for booking {booking.booking_id}")
        
        # Send notification to admin
        send_admin_cancellation_notification(booking, cancellation_reason)
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error sending cancellation email for booking {booking.booking_id}: {str(e)}")
        return False

def send_admin_cancellation_notification(booking, reason):
    """Send notification to admin when a booking is cancelled"""
    try:
        subject = f'⚠️ Booking Cancelled: {booking.name} - {booking.booking_id}'
        
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
    """Send email notification when booking status changes"""
    try:
        status_display = {
            'pending': 'Pending Review',
            'confirmed': 'Confirmed',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        
        # Format date and time
        appointment_date = booking.appointment_date.strftime('%A, %B %d, %Y')
        appointment_time = booking.appointment_time.strftime('%I:%M %p')
        
        # Calculate end time
        duration_minutes = int(booking.duration.replace('-min', ''))
        start_dt = datetime.combine(booking.appointment_date, booking.appointment_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        end_time = end_dt.strftime('%I:%M %p')
        
        subject = f'Booking Status Update - {status_display[new_status]} - {booking.booking_id}'
        
        # ALWAYS SEND EMAIL FOR STATUS CHANGE, REGARDLESS OF PREVIOUS STATUS
        # Create HTML content based on status
        if new_status == 'pending':
            status_color = '#ffc107'
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
            status_color = '#28a745'
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
            status_color = '#17a2b8'
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
            # Add feedback request
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
            status_color = '#dc3545'
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
            status_color = '#6c757d'
            status_icon = 'ℹ️'
            title = f'Booking Status Updated'
            message = f"""Your booking status has been updated to <strong>{status_display[new_status]}</strong>."""
            instructions = ""
        
        # Add status change note if old_status is provided
        status_change_note = ""
        if old_status and old_status != new_status:
            status_change_note = f"""
            <div style="background: #e9ecef; padding: 10px; border-radius: 5px; margin: 10px 0; font-size: 14px;">
                <strong>Status Changed:</strong> {status_display[old_status]} → {status_display[new_status]}
            </div>
            """
        
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
        
        # Send email
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email],
        )
        email.content_subtype = "html"
        email.send()
        
        logger.info(f"✓ Status change email sent to {booking.email} - Status: {old_status} → {new_status}")
        
        # Send admin notification
        send_admin_status_notification(booking, new_status, old_status)
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error sending status change email for booking {booking.booking_id}: {str(e)}")
        return False
def send_admin_status_notification(booking, new_status, old_status):
    """Send notification to admin when booking status changes"""
    try:
        status_display = {
            'pending': 'Pending',
            'confirmed': 'Confirmed',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        
        subject = f'📊 Status Changed: {booking.name} - {status_display[new_status]}'
        
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

# Add these views for admin booking management
@staff_member_required
def admin_booking_management(request):
    """Admin view to manage bookings"""
    # Get query parameters for filtering
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    # Get all bookings
    bookings = ConsultationBooking.objects.all().order_by('-created_at')
    
    # Apply filters
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            bookings = bookings.filter(appointment_date=date_obj)
        except ValueError:
            pass
    
    # Get counts for dashboard
    total_bookings = ConsultationBooking.objects.count()
    confirmed_bookings = ConsultationBooking.objects.filter(status='confirmed').count()
    pending_bookings = ConsultationBooking.objects.filter(status='pending').count()
    cancelled_bookings = ConsultationBooking.objects.filter(status='cancelled').count()
    completed_bookings = ConsultationBooking.objects.filter(status='completed').count()
    
    context = {
        'bookings': bookings,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'today': date.today(),
        'stats': {
            'total': total_bookings,
            'confirmed': confirmed_bookings,
            'pending': pending_bookings,
            'cancelled': cancelled_bookings,
            'completed': completed_bookings,
        }
    }
    
    return render(request, 'admin/booking_management.html', context)

@staff_member_required
def admin_cancel_booking(request, booking_id):
    """Admin view to cancel a specific booking"""
    booking = get_object_or_404(ConsultationBooking, booking_id=booking_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        # Update booking status
        booking.status = 'cancelled'
        booking.cancellation_reason = reason
        booking.cancelled_at = timezone.now()
        booking.save()
        
        # Send cancellation email to client
        send_cancellation_email(booking, reason)
        send_admin_status_notification(booking, 'cancelled', 'confirmed')
        
        messages.success(request, f'Booking {booking_id} has been cancelled and notification sent to client.')
        return redirect('admin_booking_management')
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'admin/cancel_booking.html', context)

@staff_member_required
def admin_complete_booking(request, booking_id):
    """Admin view to mark a booking as completed"""
    booking = get_object_or_404(ConsultationBooking, booking_id=booking_id)
    
    if request.method == 'POST':
        # Update booking status
        old_status = booking.status
        booking.status = 'completed'
        booking.completed_at = timezone.now()
        booking.save()
        
        # Send completion notification to client
        send_status_change_email(booking, 'completed', old_status)
        send_admin_status_notification(booking, 'completed', old_status)
        
        messages.success(request, f'Booking {booking_id} has been marked as completed and notification sent to client.')
        return redirect('admin_booking_management')
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'admin/complete_booking.html', context)

@staff_member_required
def admin_mark_pending(request, booking_id):
    """Admin view to mark a booking as pending"""
    booking = get_object_or_404(ConsultationBooking, booking_id=booking_id)
    
    if request.method == 'POST':
        # Update booking status
        old_status = booking.status
        booking.status = 'pending'
        booking.pending_at = timezone.now()
        booking.save()
        
        # Send pending notification to client
        send_status_change_email(booking, 'pending', old_status)
        send_admin_status_notification(booking, 'pending', old_status)
        
        messages.success(request, f'Booking {booking_id} has been marked as pending and notification sent to client.')
        return redirect('admin_booking_management')
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'admin/mark_pending.html', context)

def get_available_slots(request):
    """API endpoint to get available slots for a specific date"""
    selected_date = request.GET.get('date')
    duration = request.GET.get('duration', '45')  # Default to 45 minutes
    
    if not selected_date:
        return JsonResponse({'error': 'No date provided'}, status=400)
    
    try:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Check if date is in the past
    if selected_date_obj < date.today():
        return JsonResponse({
            'date': selected_date,
            'duration': duration,
            'available_slots': []
        })
    
    # Get available times using linear time management
    duration_minutes = int(duration)
    
    # Working hours: 9 AM to 5 PM
    start_hour = 9
    end_hour = 17
    
    # Get current time for today's date
    now = datetime.now()
    is_today = selected_date_obj == now.date()
    
    # Get all bookings for this date
    bookings = ConsultationBooking.objects.filter(
        appointment_date=selected_date_obj
    ).exclude(status='cancelled').order_by('appointment_time')
    
    # Generate all possible start times (every 15 minutes)
    available_slots = []
    current_time = datetime.combine(selected_date_obj, datetime.min.time())
    current_time = current_time.replace(hour=start_hour, minute=0)
    end_time = current_time.replace(hour=end_hour, minute=0)
    
    # Convert duration to timedelta
    duration_td = timedelta(minutes=duration_minutes)
    
    while current_time.time() <= end_time.time():
        slot_end = current_time + duration_td
        
        # Skip if slot is in the past for today
        if is_today and current_time.time() < now.time():
            current_time += timedelta(minutes=15)
            continue
        
        # Check if slot ends before working hours end
        if slot_end.time() <= end_time.time():
            # Check if this slot overlaps with any existing booking (with 15 min buffer)
            is_available = True
            
            for booking in bookings:
                booking_start = datetime.combine(selected_date_obj, booking.appointment_time)
                booking_duration = timedelta(minutes=int(booking.duration.replace('-min', '')))
                booking_end = booking_start + booking_duration + timedelta(minutes=15)  # Add 15 min buffer
                
                # Check for overlap
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
        
        # Increment by 15 minutes for next slot
        current_time += timedelta(minutes=15)
    
    return JsonResponse({
        'date': selected_date,
        'duration': duration,
        'available_slots': available_slots,
        'working_hours': f"{start_hour}:00 - {end_hour}:00",
        'is_today': is_today,
        'current_time': now.strftime('%H:%M') if is_today else None
    })

def check_date_availability(request):
    """API endpoint to check which dates have available slots in a month"""
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    duration = request.GET.get('duration', '45')  # Get duration parameter
    
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    # Get all dates in the month
    dates = []
    current_date = start_date
    
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
            
            # Working hours: 9 AM to 5 PM
            for hour in range(9, 17):
                for minute in [0, 15, 30, 45]:
                    check_time = time(hour, minute)
                    
                    # Calculate if slot fits in working hours
                    duration_minutes = int(duration)
                    duration_td = timedelta(minutes=duration_minutes)
                    start_dt = datetime.combine(current_date, check_time)
                    end_dt = start_dt + duration_td
                    
                    if end_dt.time() <= time(17, 0):  # Ends before 5 PM
                        # Check if time is available
                        if is_time_available(current_date, check_time, duration_minutes):
                            has_availability = True
                            break
                
                if has_availability:
                    break
            
            dates.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day': current_date.day,
                'has_availability': has_availability,
                'is_past': False
            })
        
        current_date += timedelta(days=1)
    
    return JsonResponse({
        'year': year,
        'month': month,
        'duration': duration,
        'dates': dates
    })

# Helper function to check time availability
def is_time_available(date_obj, start_time, duration_minutes):
    """Check if a specific time is available"""
    from datetime import timedelta
    
    requested_start = datetime.combine(date_obj, start_time)
    requested_end = requested_start + timedelta(minutes=duration_minutes)
    
    # Get all bookings for this date
    bookings = ConsultationBooking.objects.filter(
        appointment_date=date_obj
    ).exclude(status='cancelled')
    
    for booking in bookings:
        booking_start = datetime.combine(date_obj, booking.appointment_time)
        booking_duration = timedelta(minutes=int(booking.duration.replace('-min', '')))
        booking_end = booking_start + booking_duration + timedelta(minutes=15)  # Add 15 min buffer
        
        # Check for overlap
        if (requested_start < booking_end and requested_end > booking_start):
            return False
    
    return True