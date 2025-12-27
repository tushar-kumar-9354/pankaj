// disclaimer.js
// Disclaimer Page JavaScript

// DOM Elements
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navMenu = document.getElementById('navMenu');
const mainHeader = document.getElementById('mainHeader');
const currentYearEl = document.getElementById('currentYear');

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Disclaimer page loaded');

    // Set current year in footer
    setCurrentYear();

    // Initialize mobile menu
    initMobileMenu();

    // Initialize scroll effects
    initScrollEffects();

    // Initialize animations
    initAnimations();

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

    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;

        // Add shadow on scroll
        if (currentScroll > 20) {
            mainHeader.style.boxShadow = '0 4px 20px rgba(0,0,0,0.1)';
        } else {
            mainHeader.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
        }
    });
}

// Initialize animations
function initAnimations() {
    // Animate disclaimer items on scroll
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

    // Observe disclaimer items for animation
    document.querySelectorAll('.disclaimer-item').forEach(item => {
        observer.observe(item);
    });

    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        .disclaimer-item {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }

        .disclaimer-item.animate-in {
            opacity: 1;
            transform: translateY(0);
        }

        /* Stagger animation delays */
        .disclaimer-item:nth-child(1) { transition-delay: 0.1s; }
        .disclaimer-item:nth-child(2) { transition-delay: 0.2s; }
        .disclaimer-item:nth-child(3) { transition-delay: 0.3s; }
        .disclaimer-item:nth-child(4) { transition-delay: 0.4s; }
        .disclaimer-item:nth-child(5) { transition-delay: 0.5s; }
    `;
    document.head.appendChild(style);
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
    const mainContent = document.querySelector('.disclaimer-body');
    if (mainContent) {
        mainContent.id = 'main-content';
    }

    // Add aria labels to buttons
    const buttons = document.querySelectorAll('button, .btn-cta');
    buttons.forEach((button) => {
        if (!button.getAttribute('aria-label')) {
            const text = button.textContent || button.innerText;
            if (text.trim()) {
                button.setAttribute('aria-label', text.trim());
            }
        }
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