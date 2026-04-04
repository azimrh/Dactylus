const menuToggle = document.getElementById('menuToggle');
const menuClose = document.getElementById('menuClose');
const mobileMenu = document.getElementById('mobileMenu');
const mobileOverlay = document.getElementById('mobileOverlay');
const mobileNav = document.getElementById('mobileNav');
const mainNav = document.getElementById('mainNav');
const body = document.body;

// Клонируем пункты меню из десктопной версии в мобильную
function cloneNavItems() {
    if (!mobileNav || !mainNav) return;

    mobileNav.innerHTML = '';
    const links = mainNav.querySelectorAll('.d-nav__link');

    links.forEach(link => {
        // Пропускаем мобильные-only ссылки (они уже есть в десктопе)
        if (link.classList.contains('d-nav__link--mobile')) return;

        const clone = link.cloneNode(true);
        clone.classList.add('d-mobile-nav__link');
        clone.classList.remove('d-nav__link');

        // Добавляем иконки для мобильного меню
        const iconMap = {
            'Словарь': 'bi-book',
            'Мой словарь': 'bi-bookmark',
            'Поиск': 'bi-search'
        };

        const text = clone.textContent.trim();
        const iconClass = iconMap[text] || 'bi-circle';

        clone.innerHTML = `<i class="bi ${iconClass}"></i><span>${text}</span>`;
        mobileNav.appendChild(clone);
    });

    // Добавляем мобильные-only ссылки
    const mobileOnlyLinks = mainNav.querySelectorAll('.d-nav__link--mobile');
    mobileOnlyLinks.forEach(link => {
        const clone = link.cloneNode(true);
        clone.classList.add('d-mobile-nav__link');
        clone.classList.remove('d-nav__link', 'd-nav__link--mobile');

        const text = clone.textContent.trim();
        const iconClass = 'bi-search';

        clone.innerHTML = `<i class="bi ${iconClass}"></i><span>${text}</span>`;
        mobileNav.appendChild(clone);
    });
}

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

// Инициализация
if (mobileNav && mainNav) {
    cloneNavItems();
}

if (menuToggle && mobileMenu && mobileOverlay) {
    menuToggle.addEventListener('click', () => {
        if (mobileMenu.classList.contains('is-open')) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    if (menuClose) {
        menuClose.addEventListener('click', closeMenu);
    }
    mobileOverlay.addEventListener('click', closeMenu);

    const mobileLinks = mobileMenu.querySelectorAll('a');
    mobileLinks.forEach(link => {
        link.addEventListener('click', closeMenu);
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && mobileMenu.classList.contains('is-open')) {
            closeMenu();
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 991 && mobileMenu.classList.contains('is-open')) {
            closeMenu();
        }
    });
}