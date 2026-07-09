document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initAllGestureSwitchers();
    initAllSpeedControls();
});

/* ============================================
 *  TABS
 *  ============================================ */

function initTabs() {
    const tabsNav = document.querySelector('.content-tabs__nav');
    const track = document.getElementById('tabsTrack');
    if (!tabsNav || !track) return;

    const tabButtons = tabsNav.querySelectorAll('.content-tabs__btn');
    const tabPanels = track.querySelectorAll('.tab-panel');

    track.style.position = 'relative';
    track.style.minHeight = '400px';

    tabPanels.forEach((panel) => {
        panel.style.position = 'absolute';
        panel.style.top = '0';
        panel.style.left = '0';
        panel.style.width = '100%';
        panel.style.transition = 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1)';

        if (panel.classList.contains('active')) {
            panel.style.transform = 'translateX(0)';
            panel.style.opacity = '1';
            panel.style.zIndex = '1';
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

        const currentIndex = Array.from(tabPanels).indexOf(currentPanel);
        const nextIndex = Array.from(tabPanels).indexOf(nextPanel);
        const direction = nextIndex > currentIndex ? 1 : -1;

        tabButtons.forEach(b => b.classList.remove('content-tabs__btn--active'));
        btn.classList.add('content-tabs__btn--active');

        const nextPanelStartX = direction * 100;
        const currentPanelEndX = -direction * 100;

        nextPanel.style.transform = `translateX(${nextPanelStartX}%)`;
        nextPanel.style.opacity = '0';
        nextPanel.style.zIndex = '2';
        nextPanel.style.display = 'block';

        nextPanel.offsetHeight; // force reflow

        currentPanel.style.transform = `translateX(${currentPanelEndX}%)`;
        currentPanel.style.opacity = '0';
        currentPanel.style.zIndex = '1';

        nextPanel.style.transform = 'translateX(0)';
        nextPanel.style.opacity = '1';

        track.style.minHeight = nextPanel.offsetHeight + 'px';

        setTimeout(() => {
            currentPanel.classList.remove('active');
            currentPanel.style.zIndex = '0';
            currentPanel.style.display = 'none';
            nextPanel.classList.add('active');
            nextPanel.style.zIndex = '1';
        }, 400);
    });
}

/* ============================================
 *  GESTURE SWITCHER (per tab)
 *  ============================================ */

function initAllGestureSwitchers() {
    document.querySelectorAll('.gesture-switcher').forEach(switcher => {
        const panel = switcher.closest('.tab-panel');
        if (!panel) return;

        const playerEl = panel.querySelector('.d-video-player');
        if (!playerEl) return;

        // Инициализируем плеер для этой вкладки
        let player = playerEl._dactylusPlayer;
        if (!player && typeof DactylusPlayer !== 'undefined') {
            player = new DactylusPlayer(playerEl);
            playerEl._dactylusPlayer = player;
        }

        switcher.addEventListener('click', (e) => {
            const btn = e.target.closest('.gesture-switcher__btn');
            if (!btn) return;

            // Обновляем активную кнопку только внутри этого свитчера
            switcher.querySelectorAll('.gesture-switcher__btn').forEach(b => {
                b.classList.remove('gesture-switcher__btn--active');
            });
            btn.classList.add('gesture-switcher__btn--active');

            // Меняем видео в плеере ТЕКУЩЕЙ вкладки
            const videoUrl = btn.dataset.videoUrl;
            const posterUrl = btn.dataset.poster;

            if (videoUrl && player) {
                player.setVideo(videoUrl, posterUrl);
            } else if (videoUrl && playerEl.tagName === 'VIDEO') {
                // Fallback если нет DactylusPlayer
                playerEl.src = videoUrl;
                if (posterUrl) playerEl.poster = posterUrl;
                playerEl.load();
            }
        });
    });
}

/* ============================================
 *  SPEED CONTROL (per tab)
 *  ============================================ */

function initAllSpeedControls() {
    document.querySelectorAll('.speed-control').forEach(control => {
        const slider = control.querySelector('.speed-slider');
        const valueDisplay = control.querySelector('.speed-control__value');
        const panel = control.closest('.tab-panel');
        if (!panel || !slider || !valueDisplay) return;

        const video = panel.querySelector('video');
        if (!video) return;

        slider.addEventListener('input', () => {
            const speed = parseFloat(slider.value);
            video.playbackRate = speed;
            valueDisplay.textContent = speed + 'x';
        });
    });
}