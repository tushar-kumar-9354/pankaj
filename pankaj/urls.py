# urls.py
from django.urls import path
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

]