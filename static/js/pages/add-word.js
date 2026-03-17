/**
 * Add Word/Category - AJAX search functionality
 */
document.addEventListener('DOMContentLoaded', () => {
    // File upload preview
    initFileUpload();

    // AJAX search selects
    initSearchSelects();
});

function initFileUpload() {
    document.querySelectorAll('.upload-area input[type="file"]').forEach(input => {
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const area = input.closest('.upload-area');
            const placeholder = area.querySelector('.upload-area__placeholder');

            const preview = document.createElement('div');
            preview.className = 'upload-preview';

            const removeBtn = document.createElement('button');
            removeBtn.className = 'upload-preview__remove';
            removeBtn.innerHTML = '<i class="bi bi-x-lg"></i>';
            removeBtn.onclick = () => {
                preview.remove();
                input.value = '';
                placeholder.style.display = '';
            };

            if (file.type.startsWith('video/')) {
                const video = document.createElement('video');
                video.src = URL.createObjectURL(file);
                video.controls = true;
                preview.appendChild(video);
            } else if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                preview.appendChild(img);
            }

            preview.appendChild(removeBtn);
            placeholder.style.display = 'none';
            area.appendChild(preview);
        });
    });
}

function initSearchSelects() {
    document.querySelectorAll('.search-select').forEach(select => {
        const input = select.querySelector('input');
        const dropdown = select.querySelector('.search-select__dropdown');

        if (!input || !dropdown) return;

        // Debounced AJAX search
        const debouncedSearch = debounce(async (query) => {
            if (query.length < 2) {
                dropdown.classList.remove('search-select__dropdown--visible');
                return;
            }

            const response = await fetch(`/api/v1/categories/?search=${encodeURIComponent(query)}`);
            const data = await response.json();
            const results = Array.isArray(data) ? data : data.results || [];
            renderDropdown(dropdown, results, input);

            renderDropdown(dropdown, results, input);
        }, 300);

        input.addEventListener('input', (e) => debouncedSearch(e.target.value));

        input.addEventListener('focus', () => {
            if (input.value.length >= 2) {
                dropdown.classList.add('search-select__dropdown--visible');
            }
        });

        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!select.contains(e.target)) {
                dropdown.classList.remove('search-select__dropdown--visible');
            }
        });
    });
}

function renderDropdown(dropdown, results, input) {
    if (results.length === 0) {
        dropdown.innerHTML = '<div class="search-select__item">Ничего не найдено</div>';
    } else {
        dropdown.innerHTML = results.map(r => `
        <div class="search-select__item" data-id="${r.id}">
        <strong>${r.name}</strong>
        <small>${r.description}</small>
        </div>
        `).join('');
    }

    dropdown.classList.add('search-select__dropdown--visible');

    dropdown.querySelectorAll('.search-select__item[data-id]').forEach(item => {
        item.addEventListener('click', () => {
            input.value = item.querySelector('strong').textContent;
            input.dataset.selectedId = item.dataset.id;
            dropdown.classList.remove('search-select__dropdown--visible');
        });
    });
}

function debounce(fn, delay) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn.apply(this, args), delay);
    };
}
