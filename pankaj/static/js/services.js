// Services Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Initialize first tab as active
    tabContents.forEach(content => content.classList.remove('active'));
    document.getElementById('tab-compliance').classList.add('active');
    
    // Tab switching functionality
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Show corresponding content
            const tabId = button.getAttribute('data-tab');
            const targetTab = document.getElementById(`tab-${tabId}`);
            if (targetTab) {
                targetTab.classList.add('active');
                
                // Scroll to top of service detail section
                targetTab.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Service card click functionality
    const serviceLinks = document.querySelectorAll('.service-link');
    serviceLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Activate the corresponding tab
            const targetTab = document.getElementById(targetId);
            if (targetTab) {
                // Find and activate the corresponding tab button
                const tabButton = document.querySelector(`[data-tab="${targetId.replace('tab-', '')}"]`);
                if (tabButton) {
                    tabButton.classList.add('active');
                }
                
                // Show the target tab content
                targetTab.classList.add('active');
                
                // Smooth scroll to the tab content
                setTimeout(() => {
                    targetTab.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            }
        });
    });

    // Booking buttons functionality
    const bookingButtons = document.querySelectorAll('.btn-book');
    bookingButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            // In a real implementation, this would open a booking modal or redirect to contact page
            // For now, we'll scroll to contact section
            const contactLink = this.getAttribute('href');
            if (contactLink === '/contact') {
                window.location.href = '/contact';
            }
        });
    });

    // Consultation CTA button
    const consultationCTA = document.querySelector('.consultation-cta .btn-primary');
    if (consultationCTA) {
        consultationCTA.addEventListener('click', function(e) {
            e.preventDefault();
            // Switch to consultation tab
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            const consultationButton = document.querySelector('[data-tab="consultation"]');
            const consultationTab = document.getElementById('tab-consultation');
            
            if (consultationButton && consultationTab) {
                consultationButton.classList.add('active');
                consultationTab.classList.add('active');
                
                // Smooth scroll to consultation section
                setTimeout(() => {
                    consultationTab.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            }
        });
    }

    // Mobile menu toggle (if not already in script.js)
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navMenu = document.getElementById('navMenu');

    if (mobileMenuBtn && navMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            mobileMenuBtn.innerHTML = navMenu.classList.contains('active') ? 
                '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            // Check if it's a tab link
            if (targetId.startsWith('#tab-')) {
                return; // Let the tab switching handle it
            }
            
            e.preventDefault();
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add animation to service cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const serviceObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Apply animation to service elements
    const animatedElements = document.querySelectorAll('.service-card, .why-item, .pricing-card, .feature');
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        serviceObserver.observe(element);
    });

    // Pricing card hover effect enhancement
    const pricingCards = document.querySelectorAll('.pricing-card');
    pricingCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = this.classList.contains('recommended') ? 
                'scale(1.05) translateY(-10px)' : 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = this.classList.contains('recommended') ? 
                'scale(1.05)' : 'translateY(0)';
        });
    });

    // Tab button animation
    const tabButtonsAnimated = document.querySelectorAll('.tab-button');
    tabButtonsAnimated.forEach(button => {
        button.addEventListener('mouseenter', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateY(-5px)';
            }
        });
        
        button.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateY(0)';
            }
        });
    });

    // Consultation pricing interaction
    const consultationButtons = document.querySelectorAll('.consultation-options .btn-book');
    consultationButtons.forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.pricing-card');
            const planTitle = card.querySelector('h5').textContent;
            const planDuration = card.querySelector('.duration').textContent;
            const planPrice = card.querySelector('.price').textContent;
            
            // In a real implementation, this would set form values or open a modal
            console.log(`Booking ${planTitle} (${planDuration}) for ${planPrice}`);
            // Redirect to contact page with parameters
            window.location.href = `/contact?plan=${encodeURIComponent(planTitle)}&duration=${encodeURIComponent(planDuration)}&price=${encodeURIComponent(planPrice)}`;
        });
    });
});