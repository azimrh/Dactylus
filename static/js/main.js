// Mobile menu toggle
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('mobile-overlay');

    menu.classList.toggle('active');
    overlay.classList.toggle('active');

    // Prevent body scroll when menu is open
    document.body.style.overflow = menu.classList.contains('active') ? 'hidden' : '';
}

// User dropdown toggle
function toggleUserDropdown() {
    // CSS handles the hover state, this is for click support if needed
}

// Toast notifications
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span>
        <span>${message}</span>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Translator functions
function translateText() {
    const input = document.getElementById('translate-input');
    const output = document.getElementById('gesture-output');

    if (!input || !output) return;

    const text = input.value.trim();
    if (!text) {
        showToast('Введите текст для перевода', 'error');
        return;
    }

    // Simulate translation
    const words = text.split(/\s+/);
    output.innerHTML = words.map((word, i) => `
        <div class="gesture-item" onclick="playGesture('${word}')">
            <div class="gesture-thumb">🤟</div>
            <div class="gesture-text">
                <div class="gesture-token">[${word}]</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    ${i % 2 === 0 ? '✓ В вашем словаре' : '⚡ Новое слово'}
                </div>
            </div>
            <div style="color: var(--accent);">▶</div>
        </div>
    `).join('');

    showToast('Перевод выполнен', 'success');
}

function clearTranslator() {
    const input = document.getElementById('translate-input');
    const output = document.getElementById('gesture-output');
    if (input) input.value = '';
    if (output) output.innerHTML = '<p class="empty-state">Введите текст и нажмите "Перевести"</p>';
}

function playGesture(word) {
    showToast(`Воспроизведение: "${word}"`, 'success');
}

function playAll() {
    showToast('Воспроизведение всей последовательности', 'success');
}

// Personal dictionary
function addToPersonal(wordId) {
    fetch(`/personal/add/${wordId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        const btn = document.getElementById('add-btn');
        if (btn) {
            btn.textContent = '✓ В словаре';
            btn.disabled = true;
        }
        showToast('Добавлено в личный словарь', 'success');
    })
    .catch(error => {
        showToast('Ошибка при добавлении', 'error');
    });
}

function trainWord(word) {
    showToast(`Начало тренировки: "${word}"`, 'success');
}

// Moderation
function moderate(id, action) {
    showToast(`Жест ${action === 'approve' ? 'одобрен' : 'отклонен'}`, action === 'approve' ? 'success' : 'error');
    // Remove item from DOM
    event.target.closest('.queue-item').remove();
}

function showQueue(type) {
    // Update active tab
    document.querySelectorAll('.queue-tabs .tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');

    showToast(`Загружена очередь: ${type}`, 'success');
}

// Invariants
function submitAnswer(answer) {
    showToast(`Ответ принят: ${answer}`, 'success');

    // Simulate next question
    setTimeout(() => {
        const phrases = [
            { text: 'Я [люблю] чай', replace: 'предпочитаю' },
            { text: '[Большой] дом', replace: 'огромный' },
            { text: 'Идти [быстро]', replace: 'бежать' }
        ];
        const random = phrases[Math.floor(Math.random() * phrases.length)];

        const phraseEl = document.querySelector('.quiz-phrase');
        const replaceEl = document.querySelector('.replacement span');

        if (phraseEl) {
            phraseEl.innerHTML = random.text.replace(
                /\[(.*?)\]/,
                '<span class="highlight">$1</span>'
            );
        }
        if (replaceEl) {
            replaceEl.textContent = random.replace;
        }

        // Update progress
        const progressEl = document.getElementById('progress');
        if (progressEl) {
            const current = parseInt(progressEl.textContent);
            progressEl.textContent = current + 1;
        }
    }, 500);
}

// Annotation
function saveAnnotation() {
    showToast('Разметка сохранена (+10 очков)', 'success');
}

// Video speed control
function changeSpeed(value) {
    const display = document.getElementById('speed-value');
    if (display) {
        display.textContent = value + 'x';
    }
    const video = document.querySelector('.gesture-video video');
    if (video) {
        video.playbackRate = parseFloat(value);
    }
}

// Upload modal
function showUploadModal() {
    showToast('Функция загрузки в разработке', 'success');
}

// CSRF token helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Close mobile menu on resize if open
window.addEventListener('resize', () => {
    if (window.innerWidth > 1024) {
        const menu = document.getElementById('mobile-menu');
        if (menu && menu.classList.contains('active')) {
            toggleMobileMenu();
        }
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Add any initialization code here
});