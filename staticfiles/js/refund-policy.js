// refund-policy.js
// Refund Policy Page JavaScript

// DOM Elements
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navMenu = document.getElementById('navMenu');
const mainHeader = document.getElementById('mainHeader');
const currentYearEl = document.getElementById('currentYear');
const policyDateEl = document.getElementById('policyDate');

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Refund Policy page loaded');

    // Set current year in footer
    setCurrentYear();

    // Set current date for policy
    setPolicyDate();

    // Initialize mobile menu
    initMobileMenu();

    // Initialize scroll effects
    initScrollEffects();

    // Initialize animations
    initAnimations();

    // Initialize accessibility features
    initAccessibility();

    // Initialize email link handler
    initEmailLinks();
});

// Set current year in footer
function setCurrentYear() {
    if (currentYearEl) {
        currentYearEl.textContent = new Date().getFullYear();
    }
}

// Set policy date
function setPolicyDate() {
    if (policyDateEl) {
        const currentDate = new Date().toLocaleDateString('en-US', {
            month: 'long',
            year: 'numeric'
        });
        policyDateEl.textContent = currentDate;
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

        // Highlight active section based on scroll
        highlightActiveSection();
    });
}

// Highlight active section based on scroll
function highlightActiveSection() {
    const sections = document.querySelectorAll('.policy-section');
    const navLinks = document.querySelectorAll('.nav-menu a');
    const scrollPos = window.scrollY + 100;

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;

        if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
            section.classList.add('active-section');
        } else {
            section.classList.remove('active-section');
        }
    });

    // Update active nav link based on scroll position
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
}

// Initialize animations
function initAnimations() {
    // Animate policy items on scroll
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

    // Observe policy items for animation
    document.querySelectorAll('.policy-point, .exception-item, .step').forEach(item => {
        observer.observe(item);
    });

    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        .policy-point,
        .exception-item,
        .step {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }

        .policy-point.animate-in,
        .exception-item.animate-in,
        .step.animate-in {
            opacity: 1;
            transform: translateY(0);
        }

        .policy-section.active-section {
            position: relative;
        }

        .policy-section.active-section::before {
            content: '';
            position: absolute;
            left: -20px;
            top: 0;
            height: 100%;
            width: 4px;
            background: var(--accent);
            border-radius: 2px;
        }

        /* Stagger animation delays */
        .policy-point:nth-child(1) { transition-delay: 0.1s; }
        .policy-point:nth-child(2) { transition-delay: 0.2s; }
        .exception-item:nth-child(1) { transition-delay: 0.1s; }
        .exception-item:nth-child(2) { transition-delay: 0.2s; }
        .exception-item:nth-child(3) { transition-delay: 0.3s; }
        .step:nth-child(1) { transition-delay: 0.1s; }
        .step:nth-child(2) { transition-delay: 0.2s; }
        .step:nth-child(3) { transition-delay: 0.3s; }
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
    const mainContent = document.querySelector('.policy-body');
    if (mainContent) {
        mainContent.id = 'main-content';
    }

    // Add aria labels to buttons
    const buttons = document.querySelectorAll('button, .btn');
    buttons.forEach((button) => {
        if (!button.getAttribute('aria-label')) {
            const text = button.textContent || button.innerText;
            if (text.trim()) {
                button.setAttribute('aria-label', text.trim());
            }
        }
    });
}

// Initialize email links
function initEmailLinks() {
    const emailLinks = document.querySelectorAll('a[href^="mailto:"]');
    emailLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Optional: Add analytics tracking here
            console.log('Email link clicked:', this.href);
        });
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

// Add print functionality
function initPrintFunctionality() {
    // Create print button if not exists
    if (!document.getElementById('printPolicyBtn')) {
        const printBtn = document.createElement('button');
        printBtn.id = 'printPolicyBtn';
        printBtn.className = 'print-btn';
        printBtn.innerHTML = '<i class="fas fa-print"></i> Print Policy';
        printBtn.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--accent);
            color: var(--white);
            border: none;
            padding: 12px 20px;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: var(--shadow-lg);
            z-index: 999;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        `;

        printBtn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.2)';
        });

        printBtn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'var(--shadow-lg)';
        });

        printBtn.addEventListener('click', function() {
            window.print();
        });

        document.body.appendChild(printBtn);

        // Hide on print
        const printStyle = document.createElement('style');
        printStyle.textContent = `
            @media print {
                .print-btn,
                header,
                .contact-cta,
                footer {
                    display: none !important;
                }

                body {
                    padding-top: 0 !important;
                }

                .policy-card {
                    box-shadow: none !important;
                    border: 1px solid #ccc !important;
                }
            }
        `;
        document.head.appendChild(printStyle);
    }
}

// Initialize print button
initPrintFunctionality();