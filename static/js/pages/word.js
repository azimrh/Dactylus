// Tab switching with horizontal carousel
document.addEventListener('DOMContentLoaded', function() {
    const tabBtns = document.querySelectorAll('.content-tabs__btn');
    const panels = document.querySelectorAll('.tab-panel');
    let currentIndex = 0;

    function updateTabs(newIndex) {
        if (newIndex === currentIndex) return;

        const direction = newIndex > currentIndex ? 1 : -1;
        const currentPanel = panels[currentIndex];
        const newPanel = panels[newIndex];

        // Update buttons
        tabBtns.forEach((btn, i) => {
            btn.classList.toggle('content-tabs__btn--active', i === newIndex);
        });

        // Prepare new panel
        newPanel.style.display = 'block';
        newPanel.style.position = 'absolute';
        newPanel.style.top = '0';
        newPanel.style.left = '0';
        newPanel.style.width = '100%';
        newPanel.style.transform = direction > 0 ? 'translateX(100%)' : 'translateX(-100%)';
        newPanel.style.opacity = '0';
        newPanel.style.zIndex = '2';

        // Animate current panel out
        currentPanel.style.zIndex = '1';
        currentPanel.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
        currentPanel.style.transform = direction > 0 ? 'translateX(-100%)' : 'translateX(100%)';
        currentPanel.style.opacity = '0';

        // Force reflow
        newPanel.offsetHeight;

        // Animate new panel in
        requestAnimationFrame(() => {
            newPanel.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            newPanel.style.transform = 'translateX(0)';
            newPanel.style.opacity = '1';
        });

        // Cleanup after animation
        setTimeout(() => {
            currentPanel.classList.remove('active');
            currentPanel.style.display = 'none';
            currentPanel.style.position = '';
            currentPanel.style.top = '';
            currentPanel.style.left = '';
            currentPanel.style.width = '';
            currentPanel.style.transform = '';
            currentPanel.style.opacity = '';
            currentPanel.style.zIndex = '';
            currentPanel.style.transition = '';

            newPanel.classList.add('active');
            newPanel.style.position = '';
            newPanel.style.top = '';
            newPanel.style.left = '';
            newPanel.style.width = '';
            newPanel.style.transform = '';
            newPanel.style.opacity = '';
            newPanel.style.zIndex = '';
            newPanel.style.transition = '';
        }, 400);

        currentIndex = newIndex;
    }

    tabBtns.forEach((btn, index) => {
        btn.addEventListener('click', () => updateTabs(index));
    });

    // Video player functionality
    const player = document.querySelector('.d-video-player');
    const video = player?.querySelector('video');
    const playBtn = player?.querySelector('.d-video-player__play');
    const overlay = player?.querySelector('.d-video-player__overlay');
    const switcherBtns = document.querySelectorAll('.gesture-switcher__btn');

    if (video && player) {
        // Play/Pause on overlay click
        if (overlay) {
            overlay.addEventListener('click', (e) => {
                e.stopPropagation();
                togglePlay();
            });
        }

        // Play/Pause on button click
        if (playBtn) {
            playBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                togglePlay();
            });
        }

        // Video events
        video.addEventListener('play', () => {
            player.classList.remove('paused');
            if (playBtn) playBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
        });

        video.addEventListener('pause', () => {
            player.classList.add('paused');
            if (playBtn) playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
        });

        video.addEventListener('ended', () => {
            player.classList.add('paused');
            if (playBtn) playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
            video.currentTime = 0;
        });

        // Update progress
        video.addEventListener('timeupdate', updateProgress);
        video.addEventListener('loadedmetadata', updateProgress);

        // Progress bar click
        const progressContainer = player.querySelector('.video-progress');
        if (progressContainer) {
            progressContainer.addEventListener('click', (e) => {
                const rect = progressContainer.getBoundingClientRect();
                const pos = (e.clientX - rect.left) / rect.width;
                video.currentTime = pos * video.duration;
            });
        }

        function togglePlay() {
            if (video.paused) {
                video.play();
            } else {
                video.pause();
            }
        }

        function updateProgress() {
            if (!video.duration) return;

            const percent = (video.currentTime / video.duration) * 100;
            const progressBar = player.querySelector('.video-progress__bar');
            const timeDisplay = player.querySelector('.video-time');

            if (progressBar) progressBar.style.width = `${percent}%`;
            if (timeDisplay) {
                timeDisplay.textContent = `${formatTime(video.currentTime)} / ${formatTime(video.duration)}`;
            }
        }

        function formatTime(seconds) {
            if (isNaN(seconds) || !isFinite(seconds)) return '0:00';
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        }
    }

    // Gesture switching
    switcherBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const videoUrl = this.dataset.videoUrl;
            const poster = this.dataset.poster;
            const gestureId = this.dataset.gestureId;

            if (!video || !videoUrl) return;

            video.src = videoUrl;
            if (poster) video.poster = poster;

            switcherBtns.forEach(b => b.classList.remove('gesture-switcher__btn--active'));
            this.classList.add('gesture-switcher__btn--active');

            player.dataset.gestureId = gestureId;

            video.load();
            video.play().catch(() => {
                player.classList.add('paused');
            });
        });
    });

    // Speed control
    const speedSlider = document.querySelector('.speed-slider');
    const speedValue = document.querySelector('.speed-control__value');

    if (speedSlider && video) {
        speedSlider.addEventListener('input', function() {
            const speed = parseFloat(this.value);
            video.playbackRate = speed;
            speedValue.textContent = speed + 'x';
        });
    }
});

// Add to personal dictionary
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