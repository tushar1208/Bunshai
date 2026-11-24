// Services page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Animate service cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all service cards
    document.querySelectorAll('.service-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // Animate process steps
    document.querySelectorAll('.process-step').forEach((step, index) => {
        step.style.opacity = '0';
        step.style.transform = 'translateY(30px)';
        step.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;

        setTimeout(() => {
            step.style.opacity = '1';
            step.style.transform = 'translateY(0)';
        }, 300);
    });

    // Counter animation for stats (preserves suffixes like +, % and skips 24/7)
    function animateCounter(element, rawText) {
        const match = /^(\d+)([+%]?)$/.exec(rawText.trim());
        if (!match) return;
        const target = parseInt(match[1], 10);
        const suffix = match[2] || '';
        let current = 0;
        const increment = Math.max(1, target / 50);
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target + suffix;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current) + suffix;
            }
        }, 20);
    }

    // Trigger counter animation when stats section is visible
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counters = entry.target.querySelectorAll('.stat h3');
                counters.forEach(counter => {
                    animateCounter(counter, counter.textContent);
                });
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    const statsSection = document.querySelector('.stats-grid');
    if (statsSection) {
        statsObserver.observe(statsSection);
    }

    // Service card hover effects
    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Smooth scrolling for service links
    document.querySelectorAll('.service-link').forEach(link => {
        link.addEventListener('click', function(e) {
            // Add click tracking or analytics here if needed
            console.log('Service link clicked:', this.textContent.trim());
        });
    });

    // Add loading animation for service cards
    function addLoadingAnimation() {
        const cards = document.querySelectorAll('.service-card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in-up');
        });
    }

    addLoadingAnimation();

    // Handle window resize for responsive adjustments
    window.addEventListener('resize', function() {
        // Recalculate any dynamic elements if needed
        console.log('Window resized, services page responsive adjustments applied');
    });
});
