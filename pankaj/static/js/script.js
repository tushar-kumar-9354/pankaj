// script.js - COMPLETE FIXED VERSION for KP RegTech
document.addEventListener('DOMContentLoaded', function() {
    console.log('KP RegTech script loaded successfully');
    
    // ========== MOBILE MENU FUNCTIONALITY ==========
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
    
    // ========== TESTIMONIALS NAV LINK HANDLING ==========
    const testimonialLinks = document.querySelectorAll('a[href*="testimonials"], a[href="#testimonials"]');
    
    testimonialLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // If we're on homepage and clicking #testimonials
            if (href === '#testimonials' || href === '/#testimonials') {
                e.preventDefault();
                
                // Close mobile menu if open
                if (navMenu && navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    if (mobileMenuBtn) {
                        const icon = mobileMenuBtn.querySelector('i');
                        icon.classList.remove('fa-times');
                        icon.classList.add('fa-bars');
                    }
                }
                
                // Find and scroll to testimonials section
                const testimonialsSection = document.getElementById('testimonials');
                if (testimonialsSection) {
                    const headerHeight = document.querySelector('header').offsetHeight;
                    window.scrollTo({
                        top: testimonialsSection.offsetTop - headerHeight,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // ========== MOBILE DROPDOWN TOGGLE ==========
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
                parent.classList.toggle('active');
            }
        });
    });
    
    // ========== CLOSE DROPDOWNS WHEN CLICKING OUTSIDE (MOBILE) ==========
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!e.target.closest('.nav-menu') && !e.target.closest('.mobile-menu-btn')) {
                if (navMenu) navMenu.classList.remove('active');
                document.querySelectorAll('.dropdown.active, .subdropdown.active').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Reset menu icon
                if (mobileMenuBtn) {
                    const icon = mobileMenuBtn.querySelector('i');
                    if (icon) {
                        icon.classList.remove('fa-times');
                        icon.classList.add('fa-bars');
                    }
                }
            }
        }
    });
    
    // ========== SMOOTH SCROLLING FOR ANCHOR LINKS ==========
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#' || href === '#!') return;
            
            // Check if it's not a testimonials link (already handled above)
            if (href !== '#testimonials' && href !== '/#testimonials') {
                e.preventDefault();
                
                const targetElement = document.querySelector(href);
                if (targetElement) {
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
            }
        });
    });
    
    // ========== HEADER BACKGROUND ON SCROLL ==========
    window.addEventListener('scroll', function() {
        const header = document.querySelector('header');
        if (header) {
            if (window.scrollY > 100) {
                header.style.boxShadow = '0 5px 25px rgba(0,0,0,0.15)';
                header.style.backgroundColor = 'rgba(255, 255, 255, 0.98)';
            } else {
                header.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
                header.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
            }
        }
    });
    
    // ========== TESTIMONIAL CAROUSEL ==========
    const testimonialTrack = document.getElementById('testimonialTrack');
    const testimonialSlides = document.querySelectorAll('.testimonial-slide');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const dots = document.querySelectorAll('.carousel-dot');
    
    if (testimonialTrack && testimonialSlides.length > 0) {
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
        }
        
        // Go to specific slide
        function goToSlide(slideIndex) {
            // Handle wrap-around
            if (slideIndex < 0) {
                slideIndex = testimonialSlides.length - 1;
            } else if (slideIndex >= testimonialSlides.length) {
                slideIndex = 0;
            }
            
            currentSlide = slideIndex;
            updateCarousel();
        }
        
        // Update carousel display
        function updateCarousel() {
            // Move track
            testimonialTrack.style.transform = `translateX(-${currentSlide * 100}%)`;
            
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
            if (testimonialSlides.length > 1) {
                slideInterval = setInterval(() => {
                    goToSlide(currentSlide + 1);
                }, 5000); // Change slide every 5 seconds
            }
        }
        
        function stopAutoSlide() {
            if (slideInterval) {
                clearInterval(slideInterval);
            }
        }
        
        // Start the carousel
        initCarousel();
    }
    
    // ========== SCROLL ANIMATIONS ==========
    // Add CSS animation for icons
    const style = document.createElement('style');
    style.textContent = `
        @keyframes bounceIn {
            0% { opacity: 0; transform: scale(0.3) translateY(-20px); }
            50% { opacity: 0.9; transform: scale(1.05) translateY(0); }
            80% { opacity: 1; transform: scale(0.95); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        .expertise-item, .article-card {
            transition: transform 0.3s ease, opacity 0.3s ease;
        }
        
        .expertise-item.animated, .article-card.animated {
            opacity: 1;
            transform: translateY(0);
        }
    `;
    document.head.appendChild(style);
    
    // Intersection Observer for scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                
                // Special animation for expertise icons
                if (entry.target.id === 'expertise' || entry.target.classList.contains('expertise-item')) {
                    const icons = entry.target.querySelectorAll('.expertise-icon');
                    icons.forEach((icon, index) => {
                        setTimeout(() => {
                            icon.style.animation = 'bounceIn 0.6s ease forwards';
                        }, index * 200);
                    });
                }
            }
        });
    }, { 
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    // Observe elements for animation
    document.querySelectorAll('.expertise-item, .article-card, #expertise').forEach(el => {
        observer.observe(el);
    });
});

// ========== WINDOW RESIZE HANDLER ==========
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

// ========== ERROR HANDLING ==========
window.addEventListener('error', function(e) {
    console.error('Script error:', e.message, 'at', e.filename, 'line', e.lineno);
});

// ========== LOADING STATE ==========
window.addEventListener('load', function() {
    document.body.classList.add('loaded');
    console.log('Page fully loaded');
});

