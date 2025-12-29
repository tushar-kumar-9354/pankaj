from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import BlogPost, Testimonial  # We'll create these models

# Create your views here.
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

from django.db.models.functions import Lower, Trim

from django.core.paginator import Paginator

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

# views.py - Replace the entire testimonials view with this simpler version
# views.py - Update testimonials view
def testimonials(request):
    # Get all active testimonials (published ones)
    published_testimonials = Testimonial.objects.filter(is_active=True).order_by('-date_added')
    
    # Get featured testimonials for slider
    featured_testimonials = Testimonial.objects.filter(
        is_active=True, 
        is_featured=True
    ).order_by('-date_added')
    
    # Get unique industries for tabs
    industries = Testimonial.objects.filter(is_active=True).values_list(
        'industry', flat=True
    ).distinct()
    
    # Create industry data for template
    industry_data = []
    for industry in industries:
        if industry:  # Skip empty
            industry_testimonials = Testimonial.objects.filter(
                industry=industry, 
                is_active=True
            )
            if industry_testimonials.exists():
                industry_data.append({
                    'name': industry,
                    'slug': industry.lower().replace(' ', '-'),
                    'testimonials': industry_testimonials
                })
    
    # Statistics for stats section
    from django.db.models import Avg, Count
    stats = {
        'total_clients': Testimonial.objects.filter(is_active=True).count(),
        'avg_rating': round(Testimonial.objects.filter(is_active=True).aggregate(
            Avg('rating')
        )['rating__avg'] or 0, 1),
        'industries_served': Testimonial.objects.filter(is_active=True).values('industry').distinct().count(),
    }
    
    video_testimonials = Testimonial.objects.filter(
        is_active=True,
        video_url__isnull=False
    ).exclude(video_url="")
    
    context = {
        'all_testimonials': published_testimonials,
        'featured_testimonials': featured_testimonials,
        'industry_data': industry_data,
        'stats': stats,
        'video_testimonials': video_testimonials,
    }
    
    return render(request, "testimonials.html", context)
def services(request):
    return render(request,'services.html')

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
    
    context = {
        'duration': duration,
        'title': details['title'],
        'price': details['price'],
        'duration_minutes': details['duration_minutes'],
        'features': details['features'],
        'referral': request.GET.get('referral', 'service_list_widget'),
        'plan_name': plan,
        'original_duration': original_duration
    }
    
    return render(request, 'booking.html', context)

def privacy_policy(request):
    return render(request, 'privacy-policy.html')

def terms_and_conditions(request):
    return render(request, 'terms and conditions.html')

def disclaimer(request):
    return render(request, 'disclaimer.html')

def refund_policy(request):
    return render(request, 'refund-policy.html')


# views.py - Add these imports and views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import BlogPost, Testimonial, TestimonialSubmission
from .forms import TestimonialSubmissionForm

# Add this new view for submitting testimonials
# views.py - Update the submit_testimonial function
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
# Update the testimonials view to include pending submissions count
# views.py - Update the testimonials view
# views.py - Update the testimonials view
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
    from django.db.models import Avg
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


from django.http import HttpResponse
# Add to views.py
def debug_testimonials(request):
    from pankaj.models import Testimonial, TestimonialSubmission
    
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