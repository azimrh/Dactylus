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

        this.init();
    }

    init() {
        if (!this.video) return;

        // Play/Pause
        if (this.playBtn) {
            this.playBtn.addEventListener('click', () => this.togglePlay());
        }
        this.container.addEventListener('click', (e) => {
            if (e.target === this.container || e.target.closest('.d-video-player__overlay')) {
                this.togglePlay();
            }
        });

        // Progress
        this.video.addEventListener('timeupdate', () => this.updateProgress());
        this.video.addEventListener('loadedmetadata', () => this.updateProgress());
        this.video.addEventListener('ended', () => this.onEnded());

        // Click on progress bar
        const progressContainer = this.container.querySelector('.video-progress');
        if (progressContainer) {
            progressContainer.addEventListener('click', (e) => {
                const rect = progressContainer.getBoundingClientRect();
                const pos = (e.clientX - rect.left) / rect.width;
                this.video.currentTime = pos * this.video.duration;
            });
        }
    }

    togglePlay() {
        if (this.video.paused) {
            this.video.play();
            this.container.classList.remove('paused');
            if (this.playBtn) this.playBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
        } else {
            this.video.pause();
            this.container.classList.add('paused');
            if (this.playBtn) this.playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
        }
    }

    updateProgress() {
        if (!this.video.duration) return;

        const percent = (this.video.currentTime / this.video.duration) * 100;
        if (this.progressBar) this.progressBar.style.width = `${percent}%`;

        if (this.timeDisplay) {
            this.timeDisplay.textContent = `${this.formatTime(this.video.currentTime)} / ${this.formatTime(this.video.duration)}`;
        }
    }

    onEnded() {
        this.container.classList.add('paused');
        if (this.playBtn) this.playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
    }

    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    setSpeed(rate) {
        this.video.playbackRate = parseFloat(rate);
    }

    // Auto-init all players on page
    static initAll() {
        document.querySelectorAll('.d-video-player').forEach(el => new DactylusPlayer(el));
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => DactylusPlayer.initAll());
