// Blogs Page JavaScript

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
    
    // Category filtering
    const categoryLinks = document.querySelectorAll('.categories-list a');
    const postCards = document.querySelectorAll('.post-card');
    
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            categoryLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            const category = this.textContent.trim();
            
            // Filter posts based on category
            postCards.forEach(card => {
                const cardCategory = card.querySelector('.post-category').textContent.trim();
                
                if (category === 'All Posts' || cardCategory === category) {
                    card.style.display = 'grid';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
    
    // Search functionality
    const searchInput = document.querySelector('.search-box input');
    const searchButton = document.querySelector('.search-box button');
    
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase();
        
        if (searchTerm.trim() === '') return;
        
        postCards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const excerpt = card.querySelector('.post-excerpt').textContent.toLowerCase();
            const category = card.querySelector('.post-category').textContent.toLowerCase();
            
            if (title.includes(searchTerm) || excerpt.includes(searchTerm) || category.includes(searchTerm)) {
                card.style.display = 'grid';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
                
                // Highlight search term
                const titleElement = card.querySelector('h3');
                const excerptElement = card.querySelector('.post-excerpt');
                
                const highlightedTitle = highlightText(titleElement.textContent, searchTerm);
                const highlightedExcerpt = highlightText(excerptElement.textContent, searchTerm);
                
                titleElement.innerHTML = highlightedTitle;
                excerptElement.innerHTML = highlightedExcerpt;
            } else {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.display = 'none';
                }, 300);
            }
        });
    }
    
    function highlightText(text, term) {
        const regex = new RegExp(`(${term})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Sort functionality
    const sortSelect = document.querySelector('.sort-select');
    
    sortSelect.addEventListener('change', function() {
        const sortValue = this.value;
        const postsContainer = document.querySelector('.blog-posts');
        const posts = Array.from(postCards);
        
        posts.sort((a, b) => {
            const dateA = new Date(a.querySelector('.post-date').textContent.split(' ').slice(1).join(' '));
            const dateB = new Date(b.querySelector('.post-date').textContent.split(' ').slice(1).join(' '));
            
            switch(sortValue) {
                case 'latest':
                    return dateB - dateA;
                case 'oldest':
                    return dateA - dateB;
                case 'popular':
                    // For demo, using read time as popularity indicator
                    const readTimeA = parseInt(a.querySelector('.read-time').textContent);
                    const readTimeB = parseInt(b.querySelector('.read-time').textContent);
                    return readTimeB - readTimeA;
                default:
                    return 0;
            }
        });
        
        // Reorder posts in DOM
        posts.forEach(post => {
            postsContainer.appendChild(post);
        });
    });
    
    // Newsletter subscription
    const newsletterForm = document.querySelector('.newsletter-form .form-group');
    const newsletterBtn = document.querySelector('.newsletter-btn');
    
    newsletterBtn.addEventListener('click', function(e) {
        e.preventDefault();
        const emailInput = newsletterForm.querySelector('input');
        const email = emailInput.value.trim();
        
        if (validateEmail(email)) {
            // In a real application, you would send this to your server
            showNotification('Successfully subscribed to newsletter!', 'success');
            emailInput.value = '';
        } else {
            showNotification('Please enter a valid email address.', 'error');
        }
    });
    
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    function showNotification(message, type) {
        // Remove existing notification
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Style notification
        const style = document.createElement('style');
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 25px;
                border-radius: 10px;
                color: white;
                font-weight: 600;
                z-index: 10000;
                animation: slideIn 0.3s ease;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .notification.success {
                background: #000;
            }
            
            .notification.error {
                background: #dc3545;
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease forwards';
            
            const slideOutStyle = document.createElement('style');
            slideOutStyle.textContent = `
                @keyframes slideOut {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(slideOutStyle);
            
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
    
    // Post card animations
    const postCardsObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animated');
                }, index * 100);
            }
        });
    }, { threshold: 0.1 });
    
    postCards.forEach(card => {
        postCardsObserver.observe(card);
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
        if (linkPath === currentPage || (linkPath === '/blogs' && currentPage.includes('/blogs'))) {
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
        
        .post-card.animated {
            animation: fadeInUp 0.6s ease forwards;
        }
        
        mark {
            background: #ffeb3b;
            color: #000;
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        .read-article-btn i {
            transition: transform 0.3s ease;
        }
        
        .read-article-btn:hover i {
            transform: translateX(5px);
        }
        
        .read-more i {
            transition: transform 0.3s ease;
        }
        
        .read-more:hover i {
            transform: translateX(5px);
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
        
        .post-card-image img {
            transition: transform 0.5s ease, opacity 0.3s ease;
        }
    `;
    document.head.appendChild(imageStyle);
});