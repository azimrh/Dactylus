class AjaxSearch {
    constructor(options) {
        this.root = document.querySelector(options.root);
        if (!this.root) return;

        this.input = this.root.querySelector(options.input);
        this.dropdown = this.root.querySelector(options.dropdown);

        if (!this.input || !this.dropdown) return;

        // config
        this.url = options.url;
        this.minLength = options.minLength || 2;
        this.delay = options.delay || 300;
        this.mapResults = options.mapResults;
        this.renderItem = options.renderItem;
        this.onSelect = options.onSelect;

        this.debouncedSearch = this.debounce(this.search.bind(this), this.delay);

        this.init();
    }

    init() {
        this.input.addEventListener('input', (e) => {
            this.debouncedSearch(e.target.value);
        });

        this.input.addEventListener('focus', () => {
            if (this.input.value.length >= this.minLength) {
                this.show();
            }
        });

        document.addEventListener('click', (e) => {
            if (!this.root.contains(e.target)) {
                this.hide();
            }
        });
    }

    async search(query) {
        if (query.length < this.minLength) {
            this.hide();
            return;
        }

        try {
            const response = await fetch(`${this.url}${encodeURIComponent(query)}`);
            const data = await response.json();

            const results = this.mapResults
                ? this.mapResults(data)
                : data;

            this.render(results);
        } catch (e) {
            console.error('AjaxSearch error:', e);
            this.hide();
        }
    }

    render(results) {
        if (!results || results.length === 0) {
            // this.dropdown.innerHTML = `<div class="empty">Ничего не найдено</div>`;
            // this.show();
            return;
        }

        this.dropdown.innerHTML = results.map(item =>
            this.renderItem(item)
        ).join('');

        this.dropdown.querySelectorAll('[data-id]').forEach(el => {
            el.addEventListener('click', () => {
                const id = el.dataset.id;
                const text = el.dataset.text;

                if (this.onSelect) {
                    this.onSelect({ id, text, element: el });
                } else {
                    this.input.value = text;
                    this.input.dataset.selectedId = id;
                }

                this.hide();
            });
        });

        this.show();
    }

    show() {
        this.dropdown.style.display = 'block';
    }

    hide() {
        this.dropdown.style.display = 'none';
    }

    debounce(fn, delay) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn.apply(this, args), delay);
        };
    }
}