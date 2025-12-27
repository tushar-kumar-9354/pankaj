# polls/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('our_expertise/', views.our_expertise, name='our_expertise'),
    path('contact/', views.contact, name='contact'),
    path('blogs/', views.blogs, name='blogs'),
    path('testimonials/',views.testimonials, name='testimonials'),
    path('services/',views.services,name='services'),
    path('booking/<str:duration>/', views.booking, name='booking'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms and conditions', views.terms_and_conditions, name='terms_and_conditions'),
    path('refund-policy/',views.refund_policy, name='refund_policy'),
    
    path('disclaimer/',views.disclaimer, name='disclaimer'),
]
