/**
 * Moderation Page
 */
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.mod-item').forEach(item => {
        const approveBtn = item.querySelector('.mod-item__btn--approve');
        const rejectBtn = item.querySelector('.mod-item__btn--reject');
        const id = item.dataset.id;
        const type = item.dataset.type;

        if (approveBtn) {
            approveBtn.addEventListener('click', () => handleAction(id, type, 'approve', item));
        }

        if (rejectBtn) {
            rejectBtn.addEventListener('click', () => handleAction(id, type, 'reject', item));
        }
    });
});

async function handleAction(id, type, action, element) {
    try {
        // TODO: Replace with actual Django endpoint
        // await fetch(`/api/moderation/${type}/${id}/`, {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        //   body: JSON.stringify({ action })
        // });

        // Animate removal
        element.style.transform = 'translateX(100%)';
        element.style.opacity = '0';

        setTimeout(() => {
            element.remove();
            updateStats(action);
        }, 300);

    } catch (err) {
        console.error('Moderation failed:', err);
    }
}

function updateStats(action) {
    const statClass = action === 'approve' ? 'stat-card--success' : 'stat-card--danger';
    const statElement = document.querySelector(`.${statClass} .stat-card__value`);
    if (statElement) {
        const current = parseInt(statElement.textContent) || 0;
        statElement.textContent = current + 1;
    }
}
