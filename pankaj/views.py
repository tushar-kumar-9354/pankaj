from django.shortcuts import render



# Create your views here.
def index(request):
    return render(request, "index.html")
def about(request):
    return render(request, "about.html")
def our_expertise(request):
    return render(request, "our_expertise.html")
def contact(request):
    return render(request, "contact.html")
def blogs(request):
    return render(request, "blogs.html")
def testimonials(request):
    return render(request, "testimonials.html")

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

