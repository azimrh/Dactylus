/**
 * Video Player Component - Self-contained
 * Works with: .d-video-player (standard) and .video-circle (circular variant)
 * Does NOT handle: tabs, gesture switching, speed control (page-specific logic)
 */
class DactylusPlayer {
    constructor(element) {
        this.container = element;
        this.video = element.querySelector('video');
        this.playBtn = element.querySelector('.d-video-player__play');
        this.progressBar = element.querySelector('.video-progress__bar');
        this.timeDisplay = element.querySelector('.video-time');
        this.isCircular = element.classList.contains('video-circle');

        // Store instance reference on element
        element._dactylusPlayer = this;

        this.init();
    }

    init() {
        if (!this.video) return;

        // Play/Pause button
        if (this.playBtn) {
            this.playBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.togglePlay();
            });
        }

        // Click on container (only for standard player)
        if (!this.isCircular) {
            this.container.addEventListener('click', (e) => {
                const isControl = e.target.closest('.d-video-controls') ||
                                  e.target.closest('.d-video-player__play');
                if (!isControl) {
                    this.togglePlay();
                }
            });
        }

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
                e.stopPropagation();
                const rect = progressContainer.getBoundingClientRect();
                const pos = (e.clientX - rect.left) / rect.width;
                this.video.currentTime = pos * this.video.duration;
            });
        }

        // Keyboard controls
        this.container.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.togglePlay();
            }
        });

        // Make container focusable
        if (!this.container.hasAttribute('tabindex')) {
            this.container.setAttribute('tabindex', '0');
        }
    }

    togglePlay() {
        if (this.video.paused) {
            this.video.play().catch(() => {
                // Autoplay blocked or other error
            });
        } else {
            this.video.pause();
        }
    }

    onPlay() {
        this.container.classList.remove('paused');
        this.container.classList.add('playing');
        if (this.playBtn) this.playBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
    }

    onPause() {
        this.container.classList.add('paused');
        this.container.classList.remove('playing');
        if (this.playBtn) this.playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
    }

    onEnded() {
        this.container.classList.add('paused');
        this.container.classList.remove('playing');
        if (this.playBtn) this.playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
        this.video.currentTime = 0;
    }

    updateProgress() {
        if (!this.video.duration) return;

        const percent = (this.video.currentTime / this.video.duration) * 100;
        if (this.progressBar) this.progressBar.style.width = `${percent}%`;

        if (this.timeDisplay) {
            this.timeDisplay.textContent =
                `${this.formatTime(this.video.currentTime)} / ${this.formatTime(this.video.duration)}`;
        }
    }

    formatTime(seconds) {
        if (isNaN(seconds) || !isFinite(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    /**
     * Change video source
     */
    setVideo(src, poster) {
        if (!this.video) return;

        this.video.pause();
        this.video.src = src;
        if (poster) this.video.poster = poster;
        this.video.load();

        // Auto-play new video
        this.video.play().catch(() => {
            // Autoplay blocked
        });
    }

    /**
     * Set playback speed
     */
    setSpeed(speed) {
        if (this.video) {
            this.video.playbackRate = parseFloat(speed);
        }
    }

    // Auto-init all players on page
    static initAll() {
        document.querySelectorAll('.d-video-player').forEach(el => {
            if (!el._dactylusPlayer) {
                new DactylusPlayer(el);
            }
        });
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => DactylusPlayer.initAll());
} else {
    DactylusPlayer.initAll();
}