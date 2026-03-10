/**
 * Dictionary Page - AJAX filters
 */
document.addEventListener('DOMContentLoaded', () => {
    // Category filter chips
    const filterChips = document.querySelectorAll('.filter-chip[data-category]');
    filterChips.forEach(chip => {
        chip.addEventListener('click', () => {
            filterChips.forEach(c => c.classList.remove('filter-chip--active'));
            chip.classList.add('filter-chip--active');

            const category = chip.dataset.category;
            // AJAX call will be implemented in Django
            // window.location.href = `?category=${category}`;
        });
    });

    // Search with debounce
    const searchInput = document.querySelector('.d-search__input');
    if (searchInput) {
        const debouncedSearch = debounce((query) => {
            // AJAX search will be implemented in Django
            console.log('Search:', query);
        }, 300);

        searchInput.addEventListener('input', (e) => {
            debouncedSearch(e.target.value);
        });
    }
});

function debounce(fn, delay) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn.apply(this, args), delay);
    };
}
