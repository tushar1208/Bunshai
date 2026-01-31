// Enhanced animations and effects for index.html

document.addEventListener('DOMContentLoaded', function() {
    // Parallax effect for hero section
    if (document.querySelector('.video-hero')) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const hero = document.querySelector('.video-hero');
            if (hero) {
                const rate = scrolled * 0.5;
                hero.style.transform = `translate3d(0, ${rate}px, 0)`;
            }
        });
    }

    // Counter animation for statistics
    function animateCounter() {
        const counters = document.querySelectorAll('.counter');
        counters.forEach(counter => {
            const updateCount = () => {
                const target = +counter.getAttribute('data-target');
                const count = +counter.innerText.replace('+', '');
                const increment = target / 200;

                if (count < target) {
                    counter.innerText = Math.ceil(count + increment) + '+';
                    setTimeout(updateCount, 10);
                } else {
                    counter.innerText = target + '+';
                }
            };
            updateCount();
        });
    }

    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Add animation class
                entry.target.classList.add('animate-in');
                
                // Trigger counter animation for stats
                if (entry.target.classList.contains('stats-section')) {
                    animateCounter();
                }
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.service-card, .testimonial-card, .about-content, .stats-section').forEach(el => {
        observer.observe(el);
    });

    // Smooth hover effects for service cards
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.2)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        });
    });

    // Enhanced testimonial rotation
    if (document.querySelector('.testimonials-grid')) {
        let currentTestimonial = 0;
        const testimonials = document.querySelectorAll('.testimonial-card');
        
        function rotateTestimonials() {
            testimonials.forEach((testimonial, index) => {
                testimonial.style.opacity = '0.5';
                testimonial.style.transform = 'scale(0.95)';
            });
            
            testimonials[currentTestimonial].style.opacity = '1';
            testimonials[currentTestimonial].style.transform = 'scale(1)';
            
            currentTestimonial = (currentTestimonial + 1) % testimonials.length;
        }
        
        // Rotate every 5 seconds
        setInterval(rotateTestimonials, 5000);
        
        // Initial state
        rotateTestimonials();
    }

    // Particle background effect for hero section
    function createParticles() {
        const hero = document.querySelector('.video-overlay');
        if (!hero) return;
        
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.classList.add('particle');
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 4 + 1}px;
                height: ${Math.random() * 4 + 1}px;
                background: rgba(255, 255, 255, ${Math.random() * 0.3});
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: float ${Math.random() * 10 + 10}s linear infinite;
                animation-delay: ${Math.random() * 5}s;
            `;
            hero.appendChild(particle);
        }
    }

    // Add CSS for particles
    const particleStyles = document.createElement('style');
    particleStyles.textContent = `
        @keyframes float {
            0% { transform: translateY(0) rotate(0deg); opacity: 1; }
            100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
        }
        
        .animate-in {
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
        }
        
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
        
        .counter {
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--primary);
            display: inline-block;
        }
    `;
    document.head.appendChild(particleStyles);

    // Create particles on page load
    setTimeout(createParticles, 1000);

    // Interactive service cards
    const serviceLinks = document.querySelectorAll('.service-link');
    serviceLinks.forEach(link => {
        link.addEventListener('mouseenter', function(e) {
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.transform = 'translateX(10px)';
            }
        });
        
        link.addEventListener('mouseleave', function(e) {
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.transform = 'translateX(0)';
            }
        });
    });

    // Enhanced image loading
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Add scroll progress indicator
    function createScrollProgress() {
        const progressBar = document.createElement('div');
        progressBar.id = 'scroll-progress';
        progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: linear-gradient(to right, var(--primary), var(--primary-light));
            z-index: 10000;
            transition: width 0.1s ease;
        `;
        document.body.appendChild(progressBar);

        window.addEventListener('scroll', function() {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            progressBar.style.width = scrolled + '%';
        });
    }

    createScrollProgress();

    // Add keyboard navigation
    document.addEventListener('keydown', function(e) {
        // Spacebar to scroll down
        if (e.code === 'Space' && !e.target.matches('input, textarea')) {
            e.preventDefault();
            window.scrollBy({
                top: window.innerHeight * 0.8,
                behavior: 'smooth'
            });
        }
        
        // Arrow up/down for navigation
        if (e.code === 'ArrowDown') {
            e.preventDefault();
            window.scrollBy({
                top: 100,
                behavior: 'smooth'
            });
        }
        
        if (e.code === 'ArrowUp') {
            e.preventDefault();
            window.scrollBy({
                top: -100,
                behavior: 'smooth'
            });
        }
    });

    // Performance monitoring
    window.addEventListener('load', function() {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        console.log(`Page loaded in ${loadTime}ms`);
        
        // Send performance data to analytics (in a real implementation)
        if (loadTime > 3000) {
            console.warn('Page load time is high. Consider optimizing.');
        }
    });

    // Service card click tracking
    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('click', function() {
            const serviceName = this.querySelector('h3').textContent;
            console.log(`Service clicked: ${serviceName}`);
            // In a real implementation, you would send this to analytics
        });
    });
});

// Image slider functionality (from your index.js)
// This is already included in your index.html, but here's the complete version

const slider = document.getElementById('image-slider');
if (slider) {
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.getElementById('slider-prev');
    const nextBtn = document.getElementById('slider-next');
    const dotsContainer = document.getElementById('slider-dots');

    let currentSlide = 0;
    let slideWidth = slides[0].offsetWidth + 20;
    let visibleSlides = getVisibleSlides();
    let maxSlide = Math.max(0, slides.length - visibleSlides);

    // Create dots
    for (let i = 0; i <= maxSlide; i++) {
        const dot = document.createElement('div');
        dot.classList.add('dot');
        if (i === 0) dot.classList.add('active');
        dot.dataset.index = i;
        dotsContainer.appendChild(dot);
    }

    const dots = document.querySelectorAll('.dot');

    function updateSliderPosition() {
        slider.style.transform = `translateX(-${currentSlide * slideWidth}px)`;

        // Update active dot
        dots.forEach((dot, index) => {
            if (index === currentSlide) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    function getVisibleSlides() {
        const containerWidth = document.querySelector('.slider-container').offsetWidth;
        return Math.floor(containerWidth / slideWidth);
    }

    // Event listeners
    nextBtn?.addEventListener('click', function() {
        if (currentSlide < maxSlide) {
            currentSlide++;
            updateSliderPosition();
        }
    });

    prevBtn?.addEventListener('click', function() {
        if (currentSlide > 0) {
            currentSlide--;
            updateSliderPosition();
        }
    });

    // Dot navigation
    dots.forEach(dot => {
        dot.addEventListener('click', function() {
            currentSlide = parseInt(this.dataset.index);
            updateSliderPosition();
        });
    });

    // Auto slide
    let slideInterval = setInterval(() => {
        if (currentSlide < maxSlide) {
            currentSlide++;
        } else {
            currentSlide = 0;
        }
        updateSliderPosition();
    }, 5000);

    // Pause on hover
    slider.addEventListener('mouseenter', () => clearInterval(slideInterval));
    slider.addEventListener('mouseleave', () => {
        slideInterval = setInterval(() => {
            if (currentSlide < maxSlide) {
                currentSlide++;
            } else {
                currentSlide = 0;
            }
            updateSliderPosition();
        }, 5000);
    });

    // Touch support
    let startX, endX;
    slider.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        clearInterval(slideInterval);
    });

    slider.addEventListener('touchend', (e) => {
        endX = e.changedTouches[0].clientX;
        const threshold = 50;

        if (startX - endX > threshold && currentSlide < maxSlide) {
            currentSlide++;
        } else if (endX - startX > threshold && currentSlide > 0) {
            currentSlide--;
        }
        
        updateSliderPosition();
        slideInterval = setInterval(() => {
            if (currentSlide < maxSlide) {
                currentSlide++;
            } else {
                currentSlide = 0;
            }
            updateSliderPosition();
        }, 5000);
    });

    // Window resize handler
    window.addEventListener('resize', function() {
        slideWidth = slides[0].offsetWidth + 20;
        visibleSlides = getVisibleSlides();
        maxSlide = Math.max(0, slides.length - visibleSlides);
        
        // Recreate dots if needed
        if (dots.length !== maxSlide + 1) {
            dotsContainer.innerHTML = '';
            for (let i = 0; i <= maxSlide; i++) {
                const dot = document.createElement('div');
                dot.classList.add('dot');
                if (i === currentSlide) dot.classList.add('active');
                dot.dataset.index = i;
                dotsContainer.appendChild(dot);
            }
            
            // Reattach event listeners
            document.querySelectorAll('.dot').forEach(dot => {
                dot.addEventListener('click', function() {
                    currentSlide = parseInt(this.dataset.index);
                    updateSliderPosition();
                });
            });
        }
        
        if (currentSlide > maxSlide) {
            currentSlide = maxSlide;
        }
        
        updateSliderPosition();
    });
}
// Counter Animation
document.addEventListener('DOMContentLoaded', function() {
    const counters = document.querySelectorAll('.counter');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'));
                const increment = target / 100;
                let current = 0;
                
                const updateCounter = () => {
                    if (current < target) {
                        current += increment;
                        counter.textContent = Math.ceil(current);
                        setTimeout(updateCounter, 20);
                    } else {
                        counter.textContent = target;
                    }
                };
                
                updateCounter();
                observer.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => observer.observe(counter));
});
