/**
 * Translator Page
 */
document.addEventListener('DOMContentLoaded', () => {
    const swapBtn = document.querySelector('.translator-swap-btn');
    const fromSelect = document.querySelector('.translator-from');
    const toSelect = document.querySelector('.translator-to');
    const translateBtn = document.querySelector('.translator-action .btn');
    const inputArea = document.querySelector('.translator-textarea');
    const outputArea = document.querySelector('.translator-output');

    // Swap languages
    if (swapBtn) {
        swapBtn.addEventListener('click', () => {
            const temp = fromSelect.value;
            fromSelect.value = toSelect.value;
            toSelect.value = temp;
        });
    }

    // Translate
    if (translateBtn) {
        translateBtn.addEventListener('click', async () => {
            const text = inputArea.value.trim();
            if (!text) return;

            translateBtn.disabled = true;
            translateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Перевод...';

            try {
                // TODO: Replace with actual API call
                await new Promise(r => setTimeout(r, 800));

                const words = text.split(/\s+/);
                outputArea.innerHTML = words.map(word => `
                <div class="translator-result" data-word="${word}">
                <div class="translator-result__thumb">
                <i class="bi bi-hand-index"></i>
                </div>
                <span class="translator-result__word">${word}</span>
                </div>
                `).join('');

            } finally {
                translateBtn.disabled = false;
                translateBtn.innerHTML = '<i class="bi bi-translate me-2"></i>Перевести';
            }
        });
    }

    // Click on result
    if (outputArea) {
        outputArea.addEventListener('click', (e) => {
            const result = e.target.closest('.translator-result');
            if (result) {
                const word = result.dataset.word;
                window.location.href = `word.html?w=${encodeURIComponent(word)}`;
            }
        });
    }
});
