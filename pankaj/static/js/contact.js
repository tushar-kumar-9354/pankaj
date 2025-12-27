// static/js/contact.js - Form handling with success message (no backend needed for demo)
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('contactForm');
    const submitBtn = document.querySelector('.submit-btn');

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        // Loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

        // Simulate send (replace with actual fetch to backend if needed)
        setTimeout(() => {
            alert('Thank you! Your message has been sent. We will get back to you soon.');
            form.reset();
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span>Send Message</span><i class="fas fa-paper-plane"></i>';
        }, 1500);
    });
});