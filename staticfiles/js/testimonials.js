
// Testimonials Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Swiper slider
    const swiper = new Swiper('.testimonials-slider', {
        slidesPerView: 1,
        spaceBetween: 30,
        loop: true,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        breakpoints: {
            768: {
                slidesPerView: 1,
            },
            992: {
                slidesPerView: 1,
            }
        }
    });

    // Counter animation for stats
   // Replace ONLY this section in your testimonials.js file:

// Counter animation for stats - COMPLETELY FIXED
const counters = document.querySelectorAll('.stat-number');
let hasAnimated = false; // Prevent multiple animations

const animateCounters = () => {
    if (hasAnimated) return; // Only run once
    hasAnimated = true;
    
    counters.forEach(counter => {
        const targetAttr = counter.getAttribute('data-count');
        const target = parseFloat(targetAttr);
        let current = parseFloat(counter.innerText) || 0;
        
        const increment = target / 200;
        const isDecimal = targetAttr.includes('.');
        const decimals = isDecimal ? 1 : 0;
        
        function updateCounter() {
            if (current < target) {
                current += increment;
                if (current > target) current = target;
                counter.innerText = current.toFixed(decimals);
                requestAnimationFrame(updateCounter);
            } else {
                counter.innerText = target.toFixed(decimals);
            }
        }
        
        requestAnimationFrame(updateCounter);
    });
};

// Intersection Observer - FIXED
const statsSection = document.querySelector('.testimonials-stats');
if (statsSection) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !hasAnimated) {
                animateCounters();
                observer.unobserve(statsSection);
            }
        });
    }, { 
        threshold: 0.3 // Trigger when 30% visible
    });
    observer.observe(statsSection);
}    // Tab functionality for industry testimonials
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    // Sample testimonials data - UPDATED with correct structure
    const testimonialsData = {
        all: [
            {
                name: "Amit Verma",
                position: "Director, RetailChain India",
                rating: 5,
                content: "The team's expertise in retail sector compliance has been invaluable. They helped us navigate complex regulatory requirements across multiple states.",
                tags: ["Multi-state Compliance", "Retail Regulations", "GST Compliance"],
                industry: "retail"
            },
            {
                name: "Sanjay Kapoor",
                position: "CEO, Capital Bank",
                rating: 4.5,
                content: "As a banking institution, our compliance requirements are stringent. Anjali Bansal & Associates has consistently delivered accurate and timely solutions.",
                tags: ["Banking Compliance", "RBI Regulations", "Audit Support"],
                industry: "finance"
            },
            {
                name: "Deepika Singh",
                position: "CTO, DataSecure Tech",
                rating: 5,
                content: "Their understanding of technology sector compliance, especially data privacy regulations, has been exceptional. Highly recommended!",
                tags: ["Data Privacy", "Technology Compliance", "IPR Protection"],
                industry: "technology"
            },
            {
                name: "Rahul Jain",
                position: "Operations Head, AutoParts Ltd.",
                rating: 4,
                content: "Streamlined our factory compliance processes and helped us achieve significant efficiency improvements in regulatory reporting.",
                tags: ["Factory Compliance", "Labor Laws", "Environmental Regulations"],
                industry: "manufacturing"
            },
            {
                name: "Vikram Mehta",
                position: "Founder, EduTech Ventures",
                rating: 5,
                content: "From incorporation to fundraising, they guided us through every step. Their startup advisory services are top-notch.",
                tags: ["Startup Incorporation", "Fundraising", "ESOP Planning"],
                industry: "startups"
            },
            {
                name: "Anita Desai",
                position: "CFO, MedTech Solutions",
                rating: 4.5,
                content: "Healthcare sector compliance is complex, but their team made it manageable. Professional, knowledgeable, and reliable.",
                tags: ["Healthcare Compliance", "FDA Regulations", "Clinical Trials"],
                industry: "healthcare"
            }
        ],
        technology: [
            {
                name: "Deepika Singh",
                position: "CTO, DataSecure Tech",
                rating: 5,
                content: "Their understanding of technology sector compliance, especially data privacy regulations, has been exceptional. Highly recommended!",
                tags: ["Data Privacy", "Technology Compliance", "IPR Protection"]
            },
            {
                name: "Rohit Mehta",  // Added from featured slider
                position: "CFO, TechNova Solutions",
                rating: 5,
                content: "Anjali Bansal & Associates has been instrumental in guiding us through complex SEBI compliance requirements.",
                tags: ["SEBI Compliance", "Corporate Governance", "Board Meetings"]
            }
        ],
        manufacturing: [
            {
                name: "Rahul Jain",
                position: "Operations Head, AutoParts Ltd.",
                rating: 4,
                content: "Streamlined our factory compliance processes and helped us achieve significant efficiency improvements in regulatory reporting.",
                tags: ["Factory Compliance", "Labor Laws", "Environmental Regulations"]
            },
            {
                name: "Priya Sharma",  // Added from featured slider
                position: "Founder, GreenEarth Organics",
                rating: 4.5,
                content: "As a growing SME, we needed reliable compliance partners who could scale with us.",
                tags: ["SME Compliance", "ROC Filings", "Annual Returns"]
            }
        ],
        finance: [
            {
                name: "Sanjay Kapoor",
                position: "CEO, Capital Bank",
                rating: 4.5,
                content: "As a banking institution, our compliance requirements are stringent. Anjali Bansal & Associates has consistently delivered accurate and timely solutions.",
                tags: ["Banking Compliance", "RBI Regulations", "Audit Support"]
            },
            {
                name: "Arjun Patel",  // Added from featured slider
                position: "CEO, FinTech Innovations Ltd.",
                rating: 5,
                content: "The team's expertise in startup fundraising and FEMA regulations was crucial for our Series B funding round.",
                tags: ["Startup Advisory", "FEMA Compliance", "Fundraising"]
            }
        ],
        startups: [
            {
                name: "Vikram Mehta",
                position: "Founder, EduTech Ventures",
                rating: 5,
                content: "From incorporation to fundraising, they guided us through every step. Their startup advisory services are top-notch.",
                tags: ["Startup Incorporation", "Fundraising", "ESOP Planning"]
            },
            {
                name: "Arjun Patel",
                position: "CEO, FinTech Innovations Ltd.",
                rating: 5,
                content: "The team's expertise in startup fundraising and FEMA regulations was crucial for our Series B funding round.",
                tags: ["Startup Advisory", "FEMA Compliance", "Fundraising"]
            }
        ]
    };

    // Function to create testimonial HTML - FIXED
    function createTestimonialHTML(testimonial) {
        // Create stars HTML
        let starsHTML = '';
        for (let i = 1; i <= 5; i++) {
            if (i <= Math.floor(testimonial.rating)) {
                starsHTML += '<i class="fas fa-star"></i>';
            } else if (i === Math.ceil(testimonial.rating) && testimonial.rating % 1 !== 0) {
                starsHTML += '<i class="fas fa-star-half-alt"></i>';
            }
        }
        
        // Create tags HTML
        let tagsHTML = '';
        if (testimonial.tags && testimonial.tags.length > 0) {
            tagsHTML = testimonial.tags.map(tag => `<span>${tag}</span>`).join('');
        }
        
        return `
            <div class="industry-testimonial">
                <div class="industry-testimonial-header">
                    <div class="industry-client-info">
                        <h4>${testimonial.name}</h4>
                        <p class="industry-client-position">${testimonial.position}</p>
                    </div>
                    <div class="industry-rating">
                        <div class="stars">
                            ${starsHTML}
                        </div>
                        <span>${testimonial.rating}</span>
                    </div>
                </div>
                <div class="industry-testimonial-content">
                    <p>${testimonial.content}</p>
                </div>
                <div class="industry-service-tags">
                    ${tagsHTML}
                </div>
            </div>
        `;
    }

    // Function to populate testimonials - FIXED
    function populateTestimonials(industry = 'all') {
        const container = document.querySelector(`#tab-${industry} .testimonials-grid`);
        if (!container) {
            console.error(`Container not found for industry: ${industry}`);
            return;
        }
        
        // Clear existing content
        container.innerHTML = '';
        
        // Get testimonials for this industry
        const testimonials = testimonialsData[industry] || [];
        
        if (testimonials.length === 0) {
            container.innerHTML = '<p class="no-testimonials">No testimonials available for this industry.</p>';
            return;
        }
        
        // Add each testimonial
        testimonials.forEach(testimonial => {
            container.innerHTML += createTestimonialHTML(testimonial);
        });
    }

    // Function to initialize all testimonials - FIXED
    function initializeTestimonials() {
        // Check if elements exist before populating
        const allTabs = ['all', 'technology', 'manufacturing', 'finance', 'startups'];
        
        allTabs.forEach(tab => {
            const tabElement = document.getElementById(`tab-${tab}`);
            if (tabElement) {
                populateTestimonials(tab);
            }
        });
    }

    // Initialize testimonials
    initializeTestimonials();

    // Tab switching functionality
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the tab ID
            const tabId = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
            });
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Show corresponding content
            const targetTab = document.getElementById(`tab-${tabId}`);
            if (targetTab) {
                targetTab.classList.add('active');
            }
        });
    });

    // Video modal functionality
    const videoModal = document.getElementById('videoModal');
    const closeModal = document.getElementById('closeModal');
    const videoThumbnails = document.querySelectorAll('.video-thumbnail');
    const modalTitle = document.getElementById('modalTitle');

    if (videoThumbnails.length > 0) {
        videoThumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                const videoInfo = this.nextElementSibling;
                if (videoInfo) {
                    const titleElement = videoInfo.querySelector('h4');
                    if (titleElement) {
                        modalTitle.textContent = titleElement.textContent;
                        videoModal.classList.add('active');
                        document.body.style.overflow = 'hidden';
                    }
                }
            });
        });
    }

    if (closeModal && videoModal) {
        closeModal.addEventListener('click', function() {
            videoModal.classList.remove('active');
            document.body.style.overflow = 'auto';
        });

        videoModal.addEventListener('click', function(e) {
            if (e.target === videoModal) {
                videoModal.classList.remove('active');
                document.body.style.overflow = 'auto';
            }
        });
    }

    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navMenu = document.getElementById('navMenu');

    if (mobileMenuBtn && navMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            const icon = this.querySelector('i');
            if (icon) {
                icon.className = navMenu.classList.contains('active') ? 
                    'fas fa-times' : 'fas fa-bars';
            }
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') {
                return;
            }
            
            e.preventDefault();
            const targetElement = document.querySelector(href);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                if (navMenu && navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    if (mobileMenuBtn) {
                        const icon = mobileMenuBtn.querySelector('i');
                        if (icon) {
                            icon.className = 'fas fa-bars';
                        }
                    }
                }
            }
        });
    });

    // Add animation to testimonials on scroll
    const testimonialObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                // Optionally stop observing after animation
                testimonialObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    // Apply animation to testimonials
    const elementsToAnimate = document.querySelectorAll('.industry-testimonial, .featured-testimonial, .video-item, .logo-item');
    elementsToAnimate.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        testimonialObserver.observe(item);
    });

    // Initialize the "All" tab as active
    const defaultActiveTab = document.querySelector('.tab-button[data-tab="all"]');
    if (defaultActiveTab && !defaultActiveTab.classList.contains('active')) {
        defaultActiveTab.click();
    }
});
document.querySelectorAll(".video-thumbnail").forEach(item => {
    item.addEventListener("click", () => {
        const videoUrl = item.dataset.video;
        const title = item.dataset.title;

        document.getElementById("modalTitle").innerText = title;
        document.querySelector(".video-placeholder").innerHTML = `
            <iframe width="100%" height="400"
                src="${videoUrl}"
                frameborder="0"
                allow="autoplay; encrypted-media"
                allowfullscreen>
            </iframe>
        `;

        document.getElementById("videoModal").classList.add("active");
    });
});

document.getElementById("closeModal").addEventListener("click", () => {
    document.getElementById("videoModal").classList.remove("active");
    document.querySelector(".video-placeholder").innerHTML = "";
});

document.querySelectorAll(".video-thumbnail").forEach(item => {
    item.addEventListener("click", () => {
        const videoSrc = item.dataset.video;
        const title = item.dataset.title;

        const modal = document.getElementById("videoModal");
        const video = document.getElementById("videoPlayer");
        const iframe = document.getElementById("videoIframe");

        document.getElementById("modalTitle").innerText = title;

        video.style.display = "none";
        iframe.style.display = "none";

        if (videoSrc.includes("youtube") || videoSrc.includes("vimeo")) {
            iframe.src = videoSrc;
            iframe.style.display = "block";
        } else {
            video.src = videoSrc;
            video.style.display = "block";
            video.load();
            video.play();
        }

        modal.classList.add("active");
    });
});

document.getElementById("closeModal").onclick = () => {
    const modal = document.getElementById("videoModal");
    const video = document.getElementById("videoPlayer");
    const iframe = document.getElementById("videoIframe");

    video.pause();
    video.src = "";
    iframe.src = "";
    modal.classList.remove("active");
};
// Tab functionality for industry testimonials
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

// Tab switching functionality
tabButtons.forEach(button => {
    button.addEventListener('click', function() {
        // Get the tab ID
        const tabId = this.getAttribute('data-tab');
        
        // Remove active class from all buttons and contents
        tabButtons.forEach(btn => {
            btn.classList.remove('active');
        });
        tabContents.forEach(content => {
            content.classList.remove('active');
        });
        
        // Add active class to clicked button
        this.classList.add('active');
        
        // Show corresponding content
        const targetTab = document.getElementById(`tab-${tabId}`);
        if (targetTab) {
            targetTab.classList.add('active');
        }
    });
});