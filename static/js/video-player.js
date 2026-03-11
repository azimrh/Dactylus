/**
 * Video Player Component - Self-contained
 */
class DactylusPlayer {
    constructor(element) {
        this.container = element;
        this.video = element.querySelector('video');
        this.playBtn = element.querySelector('.d-video-player__play');
        this.progressBar = element.querySelector('.video-progress__bar');
        this.timeDisplay = element.querySelector('.video-time');
        this.speedSlider = document.querySelector('.speed-slider');
        this.speedValue = document.querySelector('.speed-control__value');

        this.init();
    }

    init() {
        if (!this.video) return;

        // Play/Pause
        if (this.playBtn) {
            this.playBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.togglePlay();
            });
        }

        this.container.addEventListener('click', (e) => {
            if (e.target === this.container || e.target.closest('.d-video-player__overlay')) {
                this.togglePlay();
            }
        });

        // Video events
        this.video.addEventListener('timeupdate', () => this.updateProgress());
        this.video.addEventListener('loadedmetadata', () => this.updateProgress());
        this.video.addEventListener('ended', () => this.onEnded());
        this.video.addEventListener('play', () => this.onPlay());
        this.video.addEventListener('pause', () => this.onPause());

        // Progress bar click
        const progressContainer = this.container.querySelector('.video-progress');
        if (progressContainer) {
            progressContainer.addEventListener('click', (e) => {
                const rect = progressContainer.getBoundingClientRect();
                const pos = (e.clientX - rect.left) / rect.width;
                this.video.currentTime = pos * this.video.duration;
            });
        }

        // Speed control
        if (this.speedSlider && this.speedValue) {
            this.speedSlider.addEventListener('input', () => {
                const speed = this.speedSlider.value;
                this.video.playbackRate = parseFloat(speed);
                this.speedValue.textContent = speed + 'x';
            });
        }

        // Keyboard controls
        this.video.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.togglePlay();
            }
        });
    }

    togglePlay() {
        if (this.video.paused) {
            this.video.play();
        } else {
            this.video.pause();
        }
    }

    onPlay() {
        this.container.classList.remove('paused');
        if (this.playBtn) this.playBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
    }

    onPause() {
        this.container.classList.add('paused');
        if (this.playBtn) this.playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
    }

    onEnded() {
        this.container.classList.add('paused');
        if (this.playBtn) this.playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
        this.video.currentTime = 0;
    }

    updateProgress() {
        if (!this.video.duration) return;

        const percent = (this.video.currentTime / this.video.duration) * 100;
        if (this.progressBar) this.progressBar.style.width = `${percent}%`;

        if (this.timeDisplay) {
            this.timeDisplay.textContent = `${this.formatTime(this.video.currentTime)} / ${this.formatTime(this.video.duration)}`;
        }
    }

    formatTime(seconds) {
        if (isNaN(seconds) || !isFinite(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    setVideo(src, poster) {
        if (this.video) {
            this.video.src = src;
            if (poster) this.video.poster = poster;
            this.video.load();
            this.video.play();
        }
    }

    // Auto-init all players on page
    static initAll() {
        document.querySelectorAll('.d-video-player').forEach(el => new DactylusPlayer(el));
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => DactylusPlayer.initAll());
} else {
    DactylusPlayer.initAll();
}