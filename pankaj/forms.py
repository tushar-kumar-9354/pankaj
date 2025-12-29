# forms.py
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