# urls.py
from django.shortcuts import get_object_or_404
from django.urls import path
from flask import redirect

from pankaj.models import BlogPost
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('our_expertise/', views.our_expertise, name='our_expertise'),
    path('contact/', views.contact, name='contact'),
    path('blogs/', views.blogs, name='blogs'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('testimonials/submit/', views.submit_testimonial, name='submit_testimonial'),
    path('testimonials/thank-you/', views.thank_you_testimonial, name='thank_you_testimonial'),
    path('services/', views.services, name='services'),
    path('booking/<str:duration>/', views.booking, name='booking'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    # Admin URL - note: this won't work without proper admin setup
    path('admin-tools/approve-testimonials/', views.approve_testimonials, name='approve_testimonials'),
    path('debug-testimonials/', views.debug_testimonials, name='debug_testimonials'),
    path('api/available-slots/', views.get_available_slots, name='available_slots'),
    path('api/date-availability/', views.check_date_availability, name='date_availability'),
    
    # Booking form submission
    path('booking/<str:duration>/submit/', views.booking, name='submit_booking'),
    path('admin/bookings/', views.admin_booking_management, name='admin_booking_management'),
    path('admin/bookings/cancel/<uuid:booking_id>/', views.admin_cancel_booking, name='admin_cancel_booking'),
   
]
def blog_detail_by_id(request, blog_id):
    """Fallback view for blog posts accessed by ID instead of slug"""
    blog = get_object_or_404(BlogPost, id=blog_id, is_published=True)
    # Redirect to the proper slug-based URL
    return redirect('blog_detail', slug=blog.slug)