// script.js - SIMPLIFIED VERSION
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
    
    // Mobile dropdown toggle
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
    
    // Close mobile menu when clicking outside
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
    
    // Header shadow on scroll
    window.addEventListener('scroll', function() {
        const header = document.querySelector('header');
        if (window.scrollY > 50) {
            header.style.boxShadow = '0 5px 20px rgba(0,0,0,0.1)';
        } else {
            header.style.boxShadow = '0 2px 20px rgba(0,0,0,0.08)';
        }
    });
    
    // Close menu on link click (mobile)
    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                navMenu.classList.remove('active');
                mobileMenuBtn.querySelector('i').classList.remove('fa-times');
                mobileMenuBtn.querySelector('i').classList.add('fa-bars');
            }
        });
    });
});

// Reset on window resize
window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
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
        
        document.querySelectorAll('.dropdown.active, .subdropdown.active').forEach(item => {
            item.classList.remove('active');
        });
    }
});