# forms.py - Updated version
from django import forms
from .models import TestimonialSubmission

class TestimonialSubmissionForm(forms.ModelForm):
    terms_agreed = forms.BooleanField(
        required=True,
        label="I agree to have my testimonial displayed on the website"
    )
    
   
    
    class Meta:
        model = TestimonialSubmission
        fields = [
            'full_name',
            'email',
            'phone',
            'company_name',
            'position',
            'industry',
            'testimonial_text',
            'rating',
            'services_used',
            'profile_picture',
        ]
        widgets = {
            'testimonial_text': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Share your detailed experience (minimum 100 characters)...'
            }),
        }
        
    def clean_testimonial_text(self):
        text = self.cleaned_data.get('testimonial_text', '')
        if len(text.strip()) < 100:
            raise forms.ValidationError("Testimonial must be at least 100 characters long.")
        return text
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating:
            rating = 5  # Default to 5 if not provided
        return rating
    
    def clean(self):
        cleaned_data = super().clean()
        video_file = cleaned_data.get('video_file')
        video_url = cleaned_data.get('video_url')
        
        # Ensure only one video option is provided
        
        return cleaned_data


# forms.py - Payment Form
from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    PAYMENT_METHOD_CHOICES = [
        ('upi', 'UPI (Google Pay, PhonePe, PayTM)'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet (PayTM, PhonePe)'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'}),
        label="Select Payment Method"
    )
    
    upi_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'yourname@upi',
            'class': 'upi-input'
        }),
        label="UPI ID"
    )
    
    class Meta:
        model = Payment
        fields = ['payment_method', 'upi_id']
        
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        upi_id = cleaned_data.get('upi_id')
        
        if payment_method == 'upi' and not upi_id:
            raise forms.ValidationError("UPI ID is required for UPI payments")
        
        return cleaned_data