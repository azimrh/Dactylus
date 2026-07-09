document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchResultsWrapper = document.getElementById('searchResultsWrapper');
    const searchResultsList = document.getElementById('searchResultsList');
    const searchLoading = document.getElementById('searchLoading');
    const searchEmpty = document.getElementById('searchEmpty');
    const searchCount = document.getElementById('searchCount');
    const searchClear = document.getElementById('searchClear');
    const searchClose = document.getElementById('searchClose');

    let searchTimeout;
    let currentQuery = '';

    // Функция поиска
    async function performSearch(query) {
        if (!query || query.length < 2) {
            hideResults();
            return;
        }

        currentQuery = query;
        showLoading();

        try {
            const response = await fetch(`/api/v1/text-lexemes/?search=${encodeURIComponent(query)}&limit=10`);

            if (!response.ok) {
                throw new Error('Ошибка при поиске');
            }

            const data = await response.json();
            displayResults(data.results || []);
        } catch (error) {
            console.error('Ошибка поиска:', error);
            showError();
        }
    }

    // Отображение результатов
    function displayResults(results) {
        hideLoading();

        if (results.length === 0) {
            showEmpty();
            return;
        }

        searchCount.textContent = `Найдено: ${results.length}`;
        searchResultsList.innerHTML = '';

        results.forEach(item => {
            const resultItem = document.createElement('a');
            resultItem.href = `/dictionary/text/${item.slug}/`;
            resultItem.className = 'd-search-result-item';
            resultItem.innerHTML = `
                <div class="d-search-result-item__text">${escapeHtml(item.text)}</div>
                ${item.meaning_preview ? `<div class="d-search-result-item__desc">${escapeHtml(item.meaning_preview)}</div>` : ''}
            `;
            searchResultsList.appendChild(resultItem);
        });

        showResults();
    }

    // Вспомогательные функции
    function showResults() {
        searchResultsWrapper.style.display = 'block';
        searchEmpty.style.display = 'none';
        searchLoading.style.display = 'none';
    }

    function hideResults() {
        searchResultsWrapper.style.display = 'none';
        searchClear.style.display = 'none';
    }

    function showLoading() {
        searchLoading.style.display = 'flex';
        searchEmpty.style.display = 'none';
        searchResultsList.innerHTML = '';
        searchResultsWrapper.style.display = 'block';
    }

    function hideLoading() {
        searchLoading.style.display = 'none';
    }

    function showEmpty() {
        searchEmpty.style.display = 'block';
        searchResultsList.innerHTML = '';
        searchCount.textContent = '';
    }

    function showError() {
        searchEmpty.textContent = 'Ошибка при поиске';
        showEmpty();
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Обработчики событий
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();

        // Показываем/скрываем кнопку очистки
        searchClear.style.display = query ? 'block' : 'none';

        // Очищаем предыдущий таймаут
        clearTimeout(searchTimeout);

        if (query.length >= 2) {
            // Debounce для уменьшения количества запросов
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        } else {
            hideResults();
        }
    });

    // Кнопка очистки
    searchClear.addEventListener('click', function() {
        searchInput.value = '';
        searchClear.style.display = 'none';
        hideResults();
        searchInput.focus();
    });

    // Кнопка закрытия результатов
    searchClose.addEventListener('click', function() {
        hideResults();
    });
});