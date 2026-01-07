// terms and conditions.js
// Terms & Conditions Page JavaScript

// DOM Elements
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navMenu = document.getElementById('navMenu');
const mainHeader = document.getElementById('mainHeader');
const currentYearEl = document.getElementById('currentYear');

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Terms & Conditions page loaded');
    
    // Set current year in footer
    setCurrentYear();
    
    // Initialize mobile menu
    initMobileMenu();
    
    // Initialize scroll effects
    initScrollEffects();
    
    // Initialize animations
    initAnimations();
    
    // Initialize smooth scrolling for anchor links
    initSmoothScrolling();
    
    // Initialize print functionality
    initPrintFunctionality();
    
    // Initialize accessibility features
    initAccessibility();
});

// Set current year in footer
function setCurrentYear() {
    if (currentYearEl) {
        currentYearEl.textContent = new Date().getFullYear();
    }
}

// Mobile Menu Functionality
function initMobileMenu() {
    if (!mobileMenuBtn || !navMenu) return;
    
    // Toggle mobile menu
    mobileMenuBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleMobileMenu();
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (navMenu.classList.contains('active') && 
            !navMenu.contains(e.target) && 
            !mobileMenuBtn.contains(e.target)) {
            closeMobileMenu();
        }
    });
    
    // Close menu when clicking on a link
    navMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });
    
    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && navMenu.classList.contains('active')) {
            closeMobileMenu();
        }
    });
}

function toggleMobileMenu() {
    navMenu.classList.toggle('active');
    mobileMenuBtn.innerHTML = navMenu.classList.contains('active') 
        ? '<i class="fas fa-times"></i>' 
        : '<i class="fas fa-bars"></i>';
    
    // Toggle body scroll
    document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
    
    // Toggle aria-expanded
    mobileMenuBtn.setAttribute('aria-expanded', navMenu.classList.contains('active'));
}

function closeMobileMenu() {
    navMenu.classList.remove('active');
    mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
    document.body.style.overflow = '';
    mobileMenuBtn.setAttribute('aria-expanded', 'false');
}

// Scroll Effects
function initScrollEffects() {
    if (!mainHeader) return;
    
    let lastScroll = 0;
    const headerHeight = mainHeader.offsetHeight;
    
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        // Add shadow on scroll
        if (currentScroll > 20) {
            mainHeader.style.boxShadow = '0 4px 20px rgba(0,0,0,0.1)';
        } else {
            mainHeader.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
        }
        
        // Hide/show header on scroll (optional)
        if (currentScroll > lastScroll && currentScroll > headerHeight) {
            // Scrolling down
            mainHeader.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            mainHeader.style.transform = 'translateY(0)';
        }
        
        lastScroll = currentScroll;
        
        // Add active class to sections in view
        highlightActiveSection();
    });
}

// Highlight active section based on scroll
function highlightActiveSection() {
    const sections = document.querySelectorAll('.legal-item');
    const scrollPos = window.scrollY + 100; // Offset for header
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        
        if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
            section.classList.add('active-section');
        } else {
            section.classList.remove('active-section');
        }
    });
}

// Initialize animations
function initAnimations() {
    // Animate legal items on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe legal items for animation
    document.querySelectorAll('.legal-item').forEach(item => {
        observer.observe(item);
    });
    
    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        .legal-item {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .legal-item.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        .legal-item.active-section {
            background: rgba(0, 0, 0, 0.02);
            border-radius: 10px;
            padding: 20px;
            margin-left: -20px;
            margin-right: -20px;
        }
        
        /* Stagger animation delays */
        .legal-item:nth-child(1) { transition-delay: 0.1s; }
        .legal-item:nth-child(2) { transition-delay: 0.2s; }
        .legal-item:nth-child(3) { transition-delay: 0.3s; }
        .legal-item:nth-child(4) { transition-delay: 0.4s; }
        .legal-item:nth-child(5) { transition-delay: 0.5s; }
        .legal-item:nth-child(6) { transition-delay: 0.6s; }
    `;
    document.head.appendChild(style);
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const headerOffset = 100;
                const elementPosition = targetElement.offsetTop;
                const offsetPosition = elementPosition - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Print functionality
function initPrintFunctionality() {
    // Create print buttons if they don't exist
    const existingPrintButtons = document.querySelectorAll('.btn-print');
    
    // Add click event to all print buttons
    existingPrintButtons.forEach(button => {
        button.addEventListener('click', function() {
            window.print();
        });
    });
    
    // Add keyboard shortcut for printing (Ctrl/Cmd + P)
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
            e.preventDefault();
            window.print();
        }
    });
    
    // Add print confirmation
    window.addEventListener('beforeprint', function() {
        console.log('Printing Terms & Conditions...');
    });
    
    window.addEventListener('afterprint', function() {
        console.log('Print completed or cancelled');
    });
}

// Accessibility features
function initAccessibility() {
    // Add skip to content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-link';
    skipLink.textContent = 'Skip to main content';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 0;
        background: var(--accent);
        color: white;
        padding: 8px;
        z-index: 1001;
        text-decoration: none;
    `;
    
    skipLink.addEventListener('focus', function() {
        this.style.top = '0';
    });
    
    skipLink.addEventListener('blur', function() {
        this.style.top = '-40px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add main content id
    const mainContent = document.querySelector('.terms-body');
    if (mainContent) {
        mainContent.id = 'main-content';
    }
    
    // Add aria labels to buttons
    const buttons = document.querySelectorAll('button, .btn-cta, .btn-print');
    buttons.forEach((button, index) => {
        if (!button.getAttribute('aria-label')) {
            const text = button.textContent || button.innerText;
            if (text.trim()) {
                button.setAttribute('aria-label', text.trim());
            }
        }
    });
    
    // Add aria labels to print buttons specifically
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(button => {
        button.setAttribute('aria-label', 'Print Terms & Conditions');
    });
}

// Window resize handler
let resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        // Close mobile menu on resize to desktop
        if (window.innerWidth > 768 && navMenu.classList.contains('active')) {
            closeMobileMenu();
        }
    }, 250);
});

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        const perfData = window.performance.timing;
        const loadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log(`Page loaded in ${loadTime}ms`);
    });
}