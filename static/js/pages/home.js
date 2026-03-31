document.addEventListener('DOMContentLoaded', () => {
    initStatsAnimation();
});

function initStatsAnimation() {
    const statsSection = document.querySelector('.stats-section');
    if (!statsSection) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounters();
                observer.disconnect();
            }
        });
    }, { threshold: 0.5 });

    observer.observe(statsSection);
}

function animateCounters() {
    document.querySelectorAll('.stat__value').forEach(stat => {
        const target = parseInt(stat.dataset.value, 10);
        if (isNaN(target)) return;

        const duration = 1000;
        const start = performance.now();

        const update = (now) => {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(target * easeOut);

            stat.textContent = current.toLocaleString('ru-RU');

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        };

        requestAnimationFrame(update);
    });
}