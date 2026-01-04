// Privacy Policy Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Update current date and year
    updateDates();
    
    // Initialize cookie modal
    initCookieModal();
    
    // Form submission handling
    initContactForm();
    
    // Print and download functionality
    initPrintDownload();
    
    // Smooth scrolling for anchor links
    initSmoothScrolling();
    
    // Highlight active section while scrolling
    initScrollHighlight();
});

// Update current date and year
function updateDates() {
    // Update current year in footer
    const currentYear = new Date().getFullYear();
    const yearElement = document.getElementById('currentYear');
    if (yearElement) {
        yearElement.textContent = currentYear;
    }
    
    // Update last updated date
    const currentDate = new Date();
    const formattedDate = currentDate.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    const dateElement = document.getElementById('currentDate');
    if (dateElement) {
        dateElement.textContent = formattedDate;
    }
}

// Cookie Modal Functionality
function initCookieModal() {
    const cookieModal = document.getElementById('cookieModal');
    const cookieSettingsBtn = document.getElementById('cookieSettingsBtn');
    const modalClose = document.querySelector('.modal-close');
    const acceptAllBtn = document.getElementById('acceptAllCookies');
    const savePreferencesBtn = document.getElementById('saveCookiePreferences');
    const rejectAllBtn = document.getElementById('rejectAllCookies');
    
    if (!cookieModal || !cookieSettingsBtn) return;
    
    // Check if user has previously set preferences
    const savedPreferences = localStorage.getItem('cookiePreferences');
    if (savedPreferences) {
        const preferences = JSON.parse(savedPreferences);
        applyCookiePreferences(preferences);
    }
    
    // Open modal
    cookieSettingsBtn.addEventListener('click', () => {
        cookieModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    });
    
    // Close modal
    modalClose.addEventListener('click', () => {
        cookieModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    });
    
    // Close modal when clicking outside
    cookieModal.addEventListener('click', (e) => {
        if (e.target === cookieModal) {
            cookieModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
    
    // Accept all cookies
    if (acceptAllBtn) {
        acceptAllBtn.addEventListener('click', () => {
            document.getElementById('analyticsCookies').checked = true;
            document.getElementById('preferenceCookies').checked = true;
            saveCookiePreferences();
            showNotification('All cookies have been accepted.');
            cookieModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
    }
    
    // Save preferences
    if (savePreferencesBtn) {
        savePreferencesBtn.addEventListener('click', () => {
            saveCookiePreferences();
            showNotification('Cookie preferences saved successfully.');
            cookieModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
    }
    
    // Reject all non-essential cookies
    if (rejectAllBtn) {
        rejectAllBtn.addEventListener('click', () => {
            document.getElementById('analyticsCookies').checked = false;
            document.getElementById('preferenceCookies').checked = false;
            saveCookiePreferences();
            showNotification('Non-essential cookies have been rejected.');
            cookieModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
    }
}

function saveCookiePreferences() {
    const preferences = {
        analytics: document.getElementById('analyticsCookies').checked,
        preferences: document.getElementById('preferenceCookies').checked,
        timestamp: new Date().toISOString()
    };
    
    localStorage.setItem('cookiePreferences', JSON.stringify(preferences));
    
    // Apply preferences immediately
    applyCookiePreferences(preferences);
}

function applyCookiePreferences(preferences) {
    // Apply analytics cookies
    if (preferences.analytics) {
        // Initialize analytics tracking
        console.log('Analytics cookies enabled');
    } else {
        // Disable analytics tracking
        console.log('Analytics cookies disabled');
    }
    
    // Apply preference cookies
    if (preferences.preferences) {
        // Load user preferences
        console.log('Preference cookies enabled');
    } else {
        // Clear preference cookies
        console.log('Preference cookies disabled');
    }
}

// Contact Form Handling
function initContactForm() {
    const contactForm = document.getElementById('privacyContactForm');
    if (!contactForm) return;
    
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Basic validation
        if (!validateForm(this)) {
            return;
        }
        
        // Show loading state
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        submitBtn.disabled = true;
        
        // Simulate API call
        setTimeout(() => {
            // Show success message
            showNotification('Your message has been sent successfully! We will respond within 3-5 business days.', 'success');
            
            // Reset form
            contactForm.reset();
            
            // Reset button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            
            // Scroll to top of form
            contactForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 1500);
    });
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = '#e53e3e';
            isValid = false;
            
            // Remove error style on input
            field.addEventListener('input', () => {
                field.style.borderColor = '#e2e8f0';
            });
        }
    });
    
    // Validate email format
    const emailField = form.querySelector('input[type="email"]');
    if (emailField && emailField.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailField.value)) {
            emailField.style.borderColor = '#e53e3e';
            showNotification('Please enter a valid email address.', 'error');
            isValid = false;
        }
    }
    
    if (!isValid) {
        showNotification('Please fill in all required fields correctly.', 'error');
    }
    
    return isValid;
}

// Print and Download Functionality
function initPrintDownload() {
    const printBtn = document.getElementById('printPolicyBtn');
    const downloadBtn = document.getElementById('downloadPolicyBtn');
    
    if (printBtn) {
        printBtn.addEventListener('click', printPolicy);
    }
    
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadPolicy);
    }
}

function printPolicy() {
    // Create a printable version of the policy
    const printContent = document.querySelector('.privacy-content').cloneNode(true);
    const printWindow = window.open('', '_blank');
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Privacy Policy - KP RegTech</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1, h2, h3 { color: #1a3a5f; }
                h1 { font-size: 24px; border-bottom: 2px solid #3182ce; padding-bottom: 10px; }
                h2 { font-size: 20px; margin-top: 30px; }
                h3 { font-size: 18px; margin-top: 20px; }
                .print-header { text-align: center; margin-bottom: 40px; border-bottom: 1px solid #ccc; padding-bottom: 20px; }
                .print-date { text-align: right; color: #666; font-size: 14px; margin-top: 30px; }
                @media print {
                    .no-print { display: none; }
                    body { font-size: 12pt; }
                }
            </style>
        </head>
        <body>
            <div class="print-header">
                <h1>Privacy Policy</h1>
                <h2>KP RegTech</h2>
                <p></p>
            </div>
            ${printContent.innerHTML}
            <div class="print-date">
                <p><strong>Printed:</strong> ${new Date().toLocaleDateString()}</p>
                <p><strong>Page:</strong> ${printWindow.document.title}</p>
            </div>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
        printWindow.print();
    }, 500);
}

function downloadPolicy() {
    // Create PDF content
    const policyContent = document.querySelector('.privacy-content').innerHTML;
    const downloadContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Privacy Policy - KP RegTech</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 40px; }
                h1, h2, h3 { color: #1a3a5f; }
                h1 { font-size: 28px; border-bottom: 3px solid #3182ce; padding-bottom: 15px; text-align: center; }
                h2 { font-size: 22px; margin-top: 40px; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; }
                h3 { font-size: 18px; margin-top: 30px; color: #2c5282; }
                .pdf-header { text-align: center; margin-bottom: 50px; }
                .company-info { color: #666; font-size: 14px; margin-top: 10px; }
                .pdf-footer { margin-top: 50px; padding-top: 20px; border-top: 1px solid #ccc; color: #666; font-size: 12px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="pdf-header">
                <h1>Privacy Policy</h1>
                <h2>KP RegTech</h2>
                <p class="company-info"></p>
                <p class="company-info">Last Updated: ${new Date().toLocaleDateString()}</p>
            </div>
            ${policyContent}
            <div class="pdf-footer">
                <p>© ${new Date().getFullYear()} KP RegTech. All rights reserved.</p>
                <p>This document was downloaded on ${new Date().toLocaleDateString()}</p>
            </div>
        </body>
        </html>
    `;
    
    // Create blob and download
    const blob = new Blob([downloadContent], { type: 'text/html' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Privacy-Policy-Anjali-Bansal-${new Date().toISOString().split('T')[0]}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showNotification('Privacy policy downloaded successfully!', 'success');
}

// Smooth Scrolling
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href === '#' || href === '#!') return;
            
            e.preventDefault();
            const targetElement = document.querySelector(href);
            
            if (targetElement) {
                const headerHeight = document.querySelector('header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                // Update URL hash without scrolling
                history.pushState(null, null, href);
            }
        });
    });
}

// Scroll Highlight
function initScrollHighlight() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    if (sections.length === 0 || navLinks.length === 0) return;
    
    window.addEventListener('scroll', () => {
        let current = '';
        const scrollPosition = window.scrollY + 100;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

// Notification System
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#38a169' : type === 'error' ? '#e53e3e' : '#3182ce'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    
    // Add keyframes for animation
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            .notification-content {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            .notification-close {
                background: none;
                border: none;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
                padding: 0;
                margin-left: 10px;
                line-height: 1;
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}