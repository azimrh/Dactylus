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