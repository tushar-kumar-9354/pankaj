# urls.py
from datetime import timezone
from django.http import JsonResponse
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
    path('terms and conditions/', views.terms_and_conditions, name='terms_and_conditions'),
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
    # Payment URLs
    # path('booking/<uuid:booking_id>/payment/', views.initiate_payment, name='initiate_payment'),
    # path('payment/success/', views.payment_success, name='payment_success'),
    # path('payment/failed/', views.payment_failed, name='payment_failed'),
    # path('razorpay-webhook/', views.razorpay_webhook, name='razorpay_webhook'),
    # Test Payment URLs
path('booking/<uuid:booking_id>/payment-test/', views.initiate_payment, name='initiate_payment'),
path('payment/test/process/<str:payment_id>/', views.process_test_payment, name='process_test_payment'),
path('payment/test/success/<str:payment_id>/', views.payment_success_test, name='payment_success_test'),
path('payment/test/failed/', views.payment_failed_test, name='payment_failed_test'),
path('test-booking-flow/', views.test_booking_flow, name='test_booking_flow'),
path('booking/<uuid:booking_id>/', views.booking_detail, name='booking_detail'),
path('debug/payment-state/', views.debug_payment_state, name='debug_payment_state'),
path('test-payment-flow/', views.test_payment_flow, name='test_payment_flow'), 
# In urls.py:
path('admin/payments/verify-cash/<str:payment_id>/', views.admin_verify_cash_payment, name='admin_verify_cash_payment'),  
# Refund/Cancellation URLs
path('booking/<uuid:booking_id>/refund/', views.admin_process_refund, name='process_refund'),
path('booking/<uuid:booking_id>/cancel/', views.admin_cancel_booking, name='cancel_booking'),
path('admin/verify-cash/<str:payment_id>/', views.admin_verify_cash_payment, name='verify_cash_payment'),
path('booking/<uuid:booking_id>/download/', views.download_booking_details, name='download_booking_details'),
path('booking/test-json/', views.test_json_response, name='test_json'),
# Subscription URLs
path('blogs/verify-subscription/<str:token>/', views.verify_subscription, name='verify_subscription'),
path('blogs/unsubscribe/<str:token>/', views.unsubscribe, name='unsubscribe'),
path('debug/subscriptions/', views.debug_subscription, name='debug_subscriptions'),
path('test-email/', views.test_email_send, name='test_email'),
path('test-subscription/', views.test_subscription_form, name='test_subscription'),
path('blogs/subscribe/', views.subscribe_to_blogs, name='subscribe_to_blogs'),
]

def blog_detail_by_id(request, blog_id):
    """Fallback view for blog posts accessed by ID instead of slug"""
    blog = get_object_or_404(BlogPost, id=blog_id, is_published=True)
    # Redirect to the proper slug-based URL
    return redirect('blog_detail', slug=blog.slug)

