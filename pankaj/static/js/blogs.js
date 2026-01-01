// Blogs Page JavaScript - UPDATED

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
    
    // Category filtering
    const categoryLinks = document.querySelectorAll('.categories-list a');
    
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get category from data attribute or text
            const category = this.getAttribute('href').split('=')[1] || '';
            
            if (category) {
                // Redirect to filtered page
                const urlParams = new URLSearchParams(window.location.search);
                urlParams.set('category', category);
                window.location.href = `${window.location.pathname}?${urlParams.toString()}`;
            } else {
                // Show all posts
                window.location.href = window.location.pathname;
            }
        });
    });
    
    // Auto-submit sort form
    const sortSelect = document.querySelector('.sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            this.form.submit();
        });
    }
    
    // Search functionality
    const searchInput = document.querySelector('.search-box input');
    const searchButton = document.querySelector('.search-box button');
    
    function performSearch() {
        const searchTerm = searchInput.value.trim();
        
        if (searchTerm) {
            // For now, show alert. You can implement AJAX search later
            alert(`Search functionality will be implemented soon!\nYou searched for: "${searchTerm}"`);
            
            // To implement actual search, you'll need:
            // 1. Create a search view in Django
            // 2. Make AJAX request or redirect to search results page
            // window.location.href = `/blogs/search/?q=${encodeURIComponent(searchTerm)}`;
        }
    }
    
    if (searchButton) {
        searchButton.addEventListener('click', performSearch);
    }
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
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
    
    // Post card animations
    const postCards = document.querySelectorAll('.post-card');
    const postCardsObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    }, { threshold: 0.1 });
    
    postCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
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
    
    // Add CSS for no-featured posts
    const style = document.createElement('style');
    style.textContent = `
        .no-featured {
            color: #666;
            font-style: italic;
            text-align: center;
            padding: 20px;
        }
        
        .post-card {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        }
        
        .post-card.visible {
            opacity: 1;
            transform: translateY(0);
        }
        
        /* Pagination improvements */
        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            margin-top: 40px;
            flex-wrap: wrap;
        }
        
        .page-number, .next-page {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 40px;
            height: 40px;
            padding: 0 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            color: #333;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .page-number:hover,
        .page-number.active {
            background: #000;
            color: white;
            border-color: #000;
        }
        
        .next-page {
            gap: 8px;
        }
        
        .next-page:hover {
            background: #000;
            color: white;
            border-color: #000;
            gap: 12px;
        }
        
        /* Featured posts in sidebar */
        .featured-post {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        .featured-post:hover {
            background: white;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            transform: translateY(-5px);
        }
        
        .featured-post-content h4 {
            font-size: 1.1rem;
            color: #000;
            margin-bottom: 10px;
            line-height: 1.4;
        }
        
        .featured-post-content p {
            font-size: 0.9rem;
            line-height: 1.6;
            color: #555;
            margin-bottom: 15px;
        }
        
        .read-more {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: #000;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        
        .read-more:hover {
            gap: 12px;
            color: #333;
        }
    `;
    document.head.appendChild(style);
});
// Enhanced Parallax Effect for Blogs Hero
document.addEventListener('DOMContentLoaded', function() {
    const blogsHero = document.querySelector('.blogs-hero');
    const heroOverlay = document.querySelector('.blogs-hero .hero-overlay');
    
    if (blogsHero) {
        // Add scroll parallax effect
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * 0.5;
            
            // Parallax effect for background
            blogsHero.style.backgroundPosition = 'center ' + (-rate * 0.5) + 'px';
            
            // Fade effect for overlay on scroll
            if (heroOverlay) {
                const opacity = 0.8 + (scrolled * 0.001);
                heroOverlay.style.opacity = Math.min(opacity, 1);
            }
        });
        
        // Add mouse move parallax effect
        document.addEventListener('mousemove', function(e) {
            const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
            const yAxis = (window.innerHeight / 2 - e.pageY) / 25;
            
            blogsHero.style.transform = `translateX(${xAxis}px) translateY(${yAxis}px)`;
        });
        
        // Remove mouse move effect on mobile
        if (window.innerWidth <= 768) {
            blogsHero.style.transform = 'none';
        }
    }
    
    // Count animation for stats (if any)
    const statNumbers = document.querySelectorAll('.stat-number');
    if (statNumbers.length > 0) {
        statNumbers.forEach(stat => {
            const target = parseInt(stat.getAttribute('data-count'));
            const increment = target / 200;
            let current = 0;
            
            const updateCount = () => {
                if (current < target) {
                    current += increment;
                    stat.textContent = Math.ceil(current);
                    setTimeout(updateCount, 1);
                } else {
                    stat.textContent = target;
                }
            };
            
            // Trigger on scroll into view
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        updateCount();
                        observer.unobserve(entry.target);
                    }
                });
            });
            
            observer.observe(stat);
        });
    }
});