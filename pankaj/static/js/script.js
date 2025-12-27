// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navMenu = document.getElementById('navMenu');
    
    if (mobileMenuBtn && navMenu) {
        mobileMenuBtn.addEventListener('click', function() {
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
    
    // Parallax effect for hero section
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const hero = document.querySelector('.hero');
        
        if (hero) {
            const heroBg = hero.querySelector('.hero-bg');
            if (heroBg) {
                heroBg.style.transform = `scale(1.1) translateY(${scrolled * 0.5}px)`;
            }
        }
        
        // Parallax for belief section
        const belief = document.querySelector('.belief');
        if (belief) {
            const beliefBg = belief.querySelector('.belief-bg');
            if (beliefBg) {
                beliefBg.style.transform = `translateY(${scrolled * 0.3}px)`;
            }
        }
    });
    
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
    
    // Add hover effect for expertise items
    document.querySelectorAll('.expertise-item').forEach(item => {
        item.addEventListener('mouseenter', function() {
            const bg = this.querySelector('.expertise-bg');
            if (bg) {
                bg.style.transform = 'scale(1.05)';
                bg.style.transition = 'transform 0.5s ease';
            }
        });
        
        item.addEventListener('mouseleave', function() {
            const bg = this.querySelector('.expertise-bg');
            if (bg) {
                bg.style.transform = 'scale(1)';
            }
        });
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
    
    // Initialize carousel
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
        
        // Touch/swipe support for mobile
        let startX = 0;
        let endX = 0;
        
        if (testimonialTrack) {
            testimonialTrack.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
                stopAutoSlide();
            });
            
            testimonialTrack.addEventListener('touchmove', (e) => {
                endX = e.touches[0].clientX;
            });
            
            testimonialTrack.addEventListener('touchend', () => {
                const difference = startX - endX;
                
                if (Math.abs(difference) > 50) { // Minimum swipe distance
                    if (difference > 0) {
                        // Swiped left, go to next slide
                        goToSlide(currentSlide + 1);
                    } else {
                        // Swiped right, go to previous slide
                        goToSlide(currentSlide - 1);
                    }
                }
                
                startAutoSlide();
            });
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
        
        // Update button states
        if (prevBtn && nextBtn) {
            prevBtn.style.opacity = currentSlide === 0 ? '0.5' : '1';
            nextBtn.style.opacity = currentSlide === totalSlides - 1 ? '0.5' : '1';
        }
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
    
    // Initialize carousel if elements exist
    if (testimonialTrack && testimonialSlides.length > 0) {
        initCarousel();
    }
    
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
});