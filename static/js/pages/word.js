document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initGestureSwitcher();
    initSpeedControl();
});

function initTabs() {
    const tabsNav = document.querySelector('.content-tabs__nav');
    const track = document.getElementById('tabsTrack');
    if (!tabsNav || !track) return;

    const tabButtons = tabsNav.querySelectorAll('.content-tabs__btn');
    const tabPanels = track.querySelectorAll('.tab-panel');

    // Set track to relative positioning for absolute children
    track.style.position = 'relative';
    track.style.minHeight = '400px';

    // Initialize panels
    tabPanels.forEach((panel, index) => {
        panel.style.position = 'absolute';
        panel.style.top = '0';
        panel.style.left = '0';
        panel.style.width = '100%';
        panel.style.transition = 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1)';

        if (panel.classList.contains('active')) {
            panel.style.transform = 'translateX(0)';
            panel.style.opacity = '1';
            panel.style.zIndex = '1';
            // Set track height to active panel
            track.style.minHeight = panel.offsetHeight + 'px';
        } else {
            panel.style.transform = 'translateX(100%)';
            panel.style.opacity = '0';
            panel.style.zIndex = '0';
        }
    });

    tabsNav.addEventListener('click', (e) => {
        const btn = e.target.closest('.content-tabs__btn');
        if (!btn) return;

        const tabId = btn.dataset.tab;
        if (!tabId) return;

        const currentPanel = track.querySelector('.tab-panel.active');
        const nextPanel = document.getElementById(`tab-${tabId}`);
        if (!nextPanel || currentPanel === nextPanel) return;

        // Determine direction
        const currentIndex = Array.from(tabPanels).indexOf(currentPanel);
        const nextIndex = Array.from(tabPanels).indexOf(nextPanel);
        const direction = nextIndex > currentIndex ? 1 : -1;

        // Update active button
        tabButtons.forEach(b => b.classList.remove('content-tabs__btn--active'));
        btn.classList.add('content-tabs__btn--active');

        // Position next panel outside viewport
        nextPanel.style.transform = `translateX(${direction * 100}%)`;
        nextPanel.style.opacity = '0';
        nextPanel.style.zIndex = '2';

        // Force reflow
        nextPanel.offsetHeight;

        // Animate: current out, next in
        currentPanel.style.transform = `translateX(${-direction * 100}%)`;
        currentPanel.style.opacity = '0';
        currentPanel.style.zIndex = '1';

        nextPanel.style.transform = 'translateX(0)';
        nextPanel.style.opacity = '1';

        // Update track height
        track.style.minHeight = nextPanel.offsetHeight + 'px';

        // Cleanup after animation
        setTimeout(() => {
            currentPanel.classList.remove('active');
            currentPanel.style.zIndex = '0';

            nextPanel.classList.add('active');
            nextPanel.style.zIndex = '1';
        }, 400);
    });
}

function initGestureSwitcher() {
    const gestureSwitcher = document.querySelector('.gesture-switcher');
    const mainPlayer = document.getElementById('mainPlayer');

    if (!gestureSwitcher || !mainPlayer) return;

    // Get or create player instance
    let player = mainPlayer._dactylusPlayer;
    if (!player && typeof DactylusPlayer !== 'undefined') {
        player = new DactylusPlayer(mainPlayer);
    }

    gestureSwitcher.addEventListener('click', (e) => {
        const btn = e.target.closest('.gesture-switcher__btn');
        if (!btn) return;

        // Update active state
        gestureSwitcher.querySelectorAll('.gesture-switcher__btn').forEach(b => {
            b.classList.remove('gesture-switcher__btn--active');
        });
        btn.classList.add('gesture-switcher__btn--active');

        // Update video source
        const videoUrl = btn.dataset.videoUrl;
        const posterUrl = btn.dataset.poster;

        if (videoUrl && player) {
            player.setVideo(videoUrl, posterUrl);
        }
    });
}

function initSpeedControl() {
    const speedSlider = document.querySelector('.speed-slider');
    const speedValue = document.querySelector('.speed-control__value');
    const mainPlayer = document.getElementById('mainPlayer');

    if (!speedSlider || !speedValue || !mainPlayer) return;

    const video = mainPlayer.querySelector('video');
    if (!video) return;

    speedSlider.addEventListener('input', () => {
        const speed = parseFloat(speedSlider.value);
        video.playbackRate = speed;
        speedValue.textContent = speed + 'x';
    });
}

function addToPersonal(lemmaType, lemmaId) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                     document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';

    fetch(`/add-to-personal/${lemmaType}/${lemmaId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'added') {
            location.reload();
        }
    })
    .catch(err => console.error('Error:', err));
}