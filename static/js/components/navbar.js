// Mobile Menu Toggle
const menuToggle = document.getElementById('menuToggle');
const menuClose = document.getElementById('menuClose');
const mobileMenu = document.getElementById('mobileMenu');
const mobileOverlay = document.getElementById('mobileOverlay');
const body = document.body;

function openMenu() {
    menuToggle.classList.add('is-active');
    mobileMenu.classList.add('is-open');
    mobileOverlay.classList.add('is-active');
    menuToggle.setAttribute('aria-expanded', 'true');
    mobileMenu.setAttribute('aria-hidden', 'false');
    mobileOverlay.setAttribute('aria-hidden', 'false');
    body.classList.add('menu-open');
}

function closeMenu() {
    menuToggle.classList.remove('is-active');
    mobileMenu.classList.remove('is-open');
    mobileOverlay.classList.remove('is-active');
    menuToggle.setAttribute('aria-expanded', 'false');
    mobileMenu.setAttribute('aria-hidden', 'true');
    mobileOverlay.setAttribute('aria-hidden', 'true');
    body.classList.remove('menu-open');
}

if (menuToggle && mobileMenu && mobileOverlay) {
    // Open menu
    menuToggle.addEventListener('click', () => {
        if (mobileMenu.classList.contains('is-open')) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    // Close menu
    if (menuClose) {
        menuClose.addEventListener('click', closeMenu);
    }
    mobileOverlay.addEventListener('click', closeMenu);

    // Close on link click
    const mobileLinks = mobileMenu.querySelectorAll('a');
    mobileLinks.forEach(link => {
        link.addEventListener('click', closeMenu);
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && mobileMenu.classList.contains('is-open')) {
            closeMenu();
        }
    });

    // Close on resize to desktop
    window.addEventListener('resize', () => {
        if (window.innerWidth > 991 && mobileMenu.classList.contains('is-open')) {
            closeMenu();
        }
    });
}