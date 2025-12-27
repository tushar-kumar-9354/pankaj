// Enhanced About Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile menu
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
    document.querySelectorAll('a[href^="#"], a[href^="/#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href.startsWith('#') || href.startsWith('/#')) {
                e.preventDefault();
                
                let targetId = href;
                if (href.startsWith('/#')) {
                    targetId = href.substring(1);
                }
                
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
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
    
    // Animated counter for stats
    const statNumbers = document.querySelectorAll('.stat-number');
    
    function animateCounter(element) {
        const target = parseInt(element.getAttribute('data-count'));
        const increment = target / 50;
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 30);
    }
    
    // Observe stats for animation
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statNumber = entry.target.querySelector('.stat-number');
                if (statNumber && !statNumber.classList.contains('animated')) {
                    statNumber.classList.add('animated');
                    animateCounter(statNumber);
                }
            }
        });
    }, { threshold: 0.5 });
    
    // Observe all stat items
    document.querySelectorAll('.stat-item').forEach(item => {
        statsObserver.observe(item);
    });
    
    // Parallax effect for hero
    window.addEventListener('scroll', function() {
        const hero = document.querySelector('.about-hero');
        if (hero) {
            const scrolled = window.pageYOffset;
            const rate = scrolled * 0.5;
            hero.style.backgroundPosition = `center ${rate}px`;
        }
    });
    
    // Team member hover effects
    const teamMembers = document.querySelectorAll('.team-member');
    
    teamMembers.forEach(member => {
        const socialIcons = member.querySelectorAll('.member-social a');
        
        member.addEventListener('mouseenter', () => {
            socialIcons.forEach((icon, index) => {
                icon.style.transform = `translateY(0)`;
                icon.style.opacity = '1';
                icon.style.transitionDelay = `${index * 0.1}s`;
            });
        });
        
        member.addEventListener('mouseleave', () => {
            socialIcons.forEach(icon => {
                icon.style.transform = `translateY(10px)`;
                icon.style.opacity = '0';
                icon.style.transitionDelay = '0s';
            });
        });
    });
    
    // Step animation
    const steps = document.querySelectorAll('.step');
    
    const stepsObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateX(0)';
                }, index * 200);
            }
        });
    }, { threshold: 0.3 });
    
    steps.forEach(step => {
        step.style.opacity = '0';
        step.style.transform = 'translateX(-20px)';
        step.style.transition = 'all 0.6s ease';
        stepsObserver.observe(step);
    });
    
    // Value cards animation
    const valueCards = document.querySelectorAll('.stand-for-item, .mission-card, .vision-card');
    
    const cardsObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animated');
                }, index * 100);
            }
        });
    }, { threshold: 0.2 });
    
    valueCards.forEach(card => {
        cardsObserver.observe(card);
    });
    
    // Header scroll effect
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
    
    // Active navigation highlighting
    const currentPage = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath === currentPage || (linkPath === '/about' && currentPage.includes('/about'))) {
            link.classList.add('active');
        }
    });
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        @keyframes scaleIn {
            from {
                opacity: 0;
                transform: scale(0.9);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        .stand-for-item.animated {
            animation: fadeInUp 0.6s ease forwards;
        }
        
        .mission-card.animated, .vision-card.animated {
            animation: scaleIn 0.6s ease forwards;
        }
        
        .team-member .member-social a {
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.3s ease;
        }
        
        .team-member:hover .member-social a {
            opacity: 1;
            transform: translateY(0);
        }
        
        .stat-item.animated .stat-number {
            animation: fadeInUp 0.6s ease forwards;
        }
    `;
    document.head.appendChild(style);
    
    // Lazy loading for images
    const images = document.querySelectorAll('img:not([loading="lazy"])');
    images.forEach(img => {
        img.setAttribute('loading', 'lazy');
    });
    
    // Add loaded class to images
    window.addEventListener('load', function() {
        document.querySelectorAll('img').forEach(img => {
            if (img.complete) {
                img.classList.add('loaded');
            } else {
                img.addEventListener('load', function() {
                    this.classList.add('loaded');
                });
            }
        });
    });
    
    // Add image fade-in effect
    const imageStyle = document.createElement('style');
    imageStyle.textContent = `
        img {
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        img.loaded {
            opacity: 1;
        }
        
        .member-image img {
            transition: transform 0.5s ease, opacity 0.3s ease;
        }
    `;
    document.head.appendChild(imageStyle);
});