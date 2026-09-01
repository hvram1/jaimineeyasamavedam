// Jaimineeya Samavedam Website JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                // Update URL without jumping
                history.pushState(null, null, this.getAttribute('href'));
            }
        });
    });

    // Highlight current section in jump links
    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const id = entry.target.getAttribute('id');
            const jumpLink = document.querySelector(`.jump-links a[href="#${id}"]`);
            if (jumpLink) {
                if (entry.isIntersecting) {
                    document.querySelectorAll('.jump-links a').forEach(a => a.classList.remove('active'));
                    jumpLink.classList.add('active');
                }
            }
        });
    }, observerOptions);

    document.querySelectorAll('.sama-entry').forEach(entry => {
        observer.observe(entry);
    });

    // Audio error handling
    document.querySelectorAll('audio').forEach(audio => {
        audio.addEventListener('error', function() {
            const container = this.closest('.audio-section');
            if (container) {
                container.innerHTML = `
                    <div class="audio-pending">
                        <span>🎵</span>
                        <span>Audio coming soon</span>
                    </div>
                `;
            }
        });
    });
});
