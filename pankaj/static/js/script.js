// script.js - COMPLETE FIXED VERSION
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navMenu = document.getElementById('navMenu');
    
    if (mobileMenuBtn && navMenu) {
        mobileMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            navMenu.classList.toggle('active');
            
            // Change icon
            const icon = this.querySelector('i');
            if (icon.classList.contains('fa-bars')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }
    
    // Mobile dropdown toggle - CLICK ONLY ON MOBILE
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle, .subdropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                e.stopPropagation();
                
                const parent = this.parentElement;
                const isActive = parent.classList.contains('active');
                
                // Close all other dropdowns
                document.querySelectorAll('.dropdown.active, .subdropdown.active').forEach(item => {
                    if (item !== parent) {
                        item.classList.remove('active');
                    }
                });
                
                // Toggle current dropdown
                if (!isActive) {
                    parent.classList.add('active');
                } else {
                    parent.classList.remove('active');
                }
            }
        });
    });
    
    // Close dropdowns when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!e.target.closest('.nav-menu') && !e.target.closest('.mobile-menu-btn')) {
                navMenu.classList.remove('active');
                document.querySelectorAll('.dropdown.active, .subdropdown.active').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Reset menu icon
                if (mobileMenuBtn) {
                    const icon = mobileMenuBtn.querySelector('i');
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        }
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if(targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if(targetElement) {
                // Close mobile menu if open
                if (navMenu && navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    if (mobileMenuBtn) {
                        const icon = mobileMenuBtn.querySelector('i');
                        icon.classList.remove('fa-times');
                        icon.classList.add('fa-bars');
                    }
                }
                
                // Calculate header height for offset
                const headerHeight = document.querySelector('header').offsetHeight;
                
                // Scroll to target
                window.scrollTo({
                    top: targetElement.offsetTop - headerHeight,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Header background on scroll
    window.addEventListener('scroll', function() {
        const header = document.querySelector('header');
        if (window.scrollY > 100) {
            header.style.boxShadow = '0 5px 25px rgba(0,0,0,0.15)';
            header.style.backgroundColor = 'rgba(255, 255, 255, 0.98)';
        } else {
            header.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
            header.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
        }
    });
    
    // Testimonial Carousel
    const testimonialTrack = document.getElementById('testimonialTrack');
    const testimonialSlides = document.querySelectorAll('.testimonial-slide');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const dots = document.querySelectorAll('.carousel-dot');
    const totalSlides = testimonialSlides.length;
    let currentSlide = 0;
    let slideInterval;
    
    // Initialize carousel if elements exist
    if (testimonialTrack && testimonialSlides.length > 0) {
        initCarousel();
    }
    
    function initCarousel() {
        updateCarousel();
        startAutoSlide();
        
        // Event listeners for buttons
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                stopAutoSlide();
                goToSlide(currentSlide - 1);
                startAutoSlide();
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                stopAutoSlide();
                goToSlide(currentSlide + 1);
                startAutoSlide();
            });
        }
        
        // Event listeners for dots
        dots.forEach(dot => {
            dot.addEventListener('click', () => {
                stopAutoSlide();
                const slideIndex = parseInt(dot.getAttribute('data-index'));
                goToSlide(slideIndex);
                startAutoSlide();
            });
        });
        
        // Pause auto-slide on hover
        const carousel = document.querySelector('.testimonial-carousel');
        if (carousel) {
            carousel.addEventListener('mouseenter', stopAutoSlide);
            carousel.addEventListener('mouseleave', startAutoSlide);
        }
    }
    
    // Go to specific slide
    function goToSlide(slideIndex) {
        // Handle wrap-around
        if (slideIndex < 0) {
            slideIndex = totalSlides - 1;
        } else if (slideIndex >= totalSlides) {
            slideIndex = 0;
        }
        
        currentSlide = slideIndex;
        updateCarousel();
    }
    
    // Update carousel display
    function updateCarousel() {
        // Move track
        if (testimonialTrack) {
            testimonialTrack.style.transform = `translateX(-${currentSlide * 100}%)`;
        }
        
        // Update dots
        dots.forEach((dot, index) => {
            if (index === currentSlide) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }
    
    // Auto slide functionality
    function startAutoSlide() {
        stopAutoSlide(); // Clear any existing interval
        slideInterval = setInterval(() => {
            goToSlide(currentSlide + 1);
        }, 5000); // Change slide every 5 seconds
    }
    
    function stopAutoSlide() {
        if (slideInterval) {
            clearInterval(slideInterval);
        }
    }
    
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, observerOptions);
    
    // Observe elements to animate
    document.querySelectorAll('.expertise-item, .feature-item, .article-card').forEach(el => {
        observer.observe(el);
    });
    
    // Add CSS animation for icons
    const style = document.createElement('style');
    style.textContent = `
        @keyframes bounceIn {
            0% {
                opacity: 0;
                transform: scale(0.3) translateY(-20px);
            }
            50% {
                opacity: 0.9;
                transform: scale(1.05) translateY(0);
            }
            80% {
                opacity: 1;
                transform: scale(0.95);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }
    `;
    document.head.appendChild(style);
    
    // Add subtle animation to expertise icons on scroll
    const expertiseObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const icons = entry.target.querySelectorAll('.expertise-icon');
                icons.forEach((icon, index) => {
                    setTimeout(() => {
                        icon.style.animation = 'bounceIn 0.6s ease forwards';
                    }, index * 200);
                });
            }
        });
    }, { threshold: 0.3 });
    
    // Observe expertise section
    const expertiseSection = document.getElementById('expertise');
    if (expertiseSection) {
        expertiseObserver.observe(expertiseSection);
    }
});

// Prevent dropdowns from staying open when resizing window
window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        // Close mobile menu if open
        const navMenu = document.getElementById('navMenu');
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        
        if (navMenu) navMenu.classList.remove('active');
        if (mobileMenuBtn) {
            const icon = mobileMenuBtn.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        }
        
        // Close all dropdowns (desktop hover will reopen them)
        document.querySelectorAll('.dropdown.active, .subdropdown.active').forEach(item => {
            item.classList.remove('active');
        });
    }
});