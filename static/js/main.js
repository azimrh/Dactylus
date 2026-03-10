/**
 * DACTYLUS CORE - Minimal JS for Django integration
 * Only essential functionality that cannot be done server-side
 */

const Dactylus = {
    version: '2.0.0',

    // Initialize all components
    init() {
        this.initTheme();
        this.initNavigation();
    },

    // Theme Management - Single source of truth for entire site
    initTheme() {
        const themeKey = 'dactylus-theme';
        const savedTheme = localStorage.getItem(themeKey) || 'dark';
        this.setTheme(savedTheme);

        const toggle = document.getElementById('themeToggle');
        if (toggle) {
            toggle.addEventListener('click', () => {
                const current = document.documentElement.getAttribute('data-theme');
                const next = current === 'light' ? 'dark' : 'light';
                this.setTheme(next);
                localStorage.setItem(themeKey, next);
            });
        }
    },

    setTheme(theme) {
        if (theme === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    },

    // Navigation highlighting
    initNavigation() {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.d-nav__link').forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href.replace('.html', ''))) {
                link.classList.add('d-nav__link--active');
            }
        });
    },

    // Utility: Debounce for AJAX inputs
    debounce(fn, delay = 300) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn.apply(this, args), delay);
        };
    },

    // Utility: Format numbers
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => Dactylus.init());
