/**
 * CầuLong.com - Main JavaScript
 * Features: Dark mode, AJAX search, Compare functionality
 */

// ─── Dark Mode ───────────────────────────────────────────────────────────────

(function initDarkMode() {
    const html = document.getElementById('html-root');
    const saved = localStorage.getItem('darkMode');
    if (saved === 'true' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        html.classList.add('dark');
    }
})();

document.addEventListener('DOMContentLoaded', function () {
    const html = document.getElementById('html-root');
    const darkToggle = document.getElementById('dark-toggle');

    if (darkToggle) {
        darkToggle.addEventListener('click', function () {
            const isDark = html.classList.toggle('dark');
            localStorage.setItem('darkMode', isDark);
        });
    }

    // ─── Mobile Menu ─────────────────────────────────────────────────────────

    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function () {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // ─── Nav AJAX Search ─────────────────────────────────────────────────────

    const navSearch = document.getElementById('nav-search');
    const searchResults = document.getElementById('search-results');

    if (navSearch && searchResults) {
        let searchTimeout = null;

        navSearch.addEventListener('input', function () {
            const q = this.value.trim();
            clearTimeout(searchTimeout);

            if (q.length < 2) {
                searchResults.classList.add('hidden');
                searchResults.innerHTML = '';
                return;
            }

            searchTimeout = setTimeout(function () {
                fetch('/search?q=' + encodeURIComponent(q) + '&format=json', {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (data.length === 0) {
                        searchResults.innerHTML = '<div class="px-4 py-3 text-sm text-gray-400 dark:text-gray-500">Không tìm thấy kết quả</div>';
                    } else {
                        searchResults.innerHTML = data.slice(0, 8).map(function (item) {
                            return '<a href="/vot-cau-long/' + item.slug + '" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">' +
                                '<div class="w-10 h-10 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700">' +
                                (item.image_url && item.image_url !== '/static/img/placeholder.png'
                                    ? '<img src="' + item.image_url + '" alt="" class="w-full h-full object-contain p-0.5">'
                                    : '<div class="w-full h-full flex items-center justify-center text-gray-400 text-xs">' + item.brand[0] + '</div>') +
                                '</div>' +
                                '<div class="flex-1 min-w-0">' +
                                '<p class="text-sm font-semibold text-gray-900 dark:text-white truncate">' + item.name + '</p>' +
                                '<p class="text-xs text-gray-400 dark:text-gray-500">' + item.brand + (item.price ? ' · ' + Number(item.price).toLocaleString('vi-VN') + '₫' : '') + '</p>' +
                                '</div>' +
                                '</a>';
                        }).join('');
                    }
                    if (data.length > 0) {
                        searchResults.innerHTML += '<a href="/search?q=' + encodeURIComponent(q) + '" class="block px-4 py-2.5 text-sm text-green-600 dark:text-green-400 font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 border-t border-gray-100 dark:border-gray-700">Xem tất cả ' + data.length + ' kết quả →</a>';
                    }
                    searchResults.classList.remove('hidden');
                })
                .catch(function () {
                    searchResults.classList.add('hidden');
                });
            }, 300);
        });

        navSearch.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                window.location.href = '/search?q=' + encodeURIComponent(this.value.trim());
            }
        });

        document.addEventListener('click', function (e) {
            if (!navSearch.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.add('hidden');
            }
        });
    }

    // ─── Compare Functionality ───────────────────────────────────────────────

    initCompare();
});


// ─── Compare ─────────────────────────────────────────────────────────────────

function getCompareList() {
    try {
        return JSON.parse(localStorage.getItem('compareList') || '[]');
    } catch (e) {
        return [];
    }
}

function saveCompareList(list) {
    localStorage.setItem('compareList', JSON.stringify(list));
}

function initCompare() {
    updateCompareUI();

    // Highlight already-in-compare buttons
    const list = getCompareList();
    list.forEach(function (item) {
        const btn = document.getElementById('compare-btn-' + item.id);
        if (btn) {
            btn.classList.add('text-green-600');
        }
    });
}

function toggleCompare(id, name) {
    let list = getCompareList();
    const idx = list.findIndex(function (i) { return i.id === id; });

    if (idx > -1) {
        list.splice(idx, 1);
        const btn = document.getElementById('compare-btn-' + id);
        if (btn) btn.classList.remove('text-green-600');
    } else {
        if (list.length >= 3) {
            alert('Bạn chỉ có thể so sánh tối đa 3 vợt cùng lúc.');
            return;
        }
        list.push({ id: id, name: name });
        const btn = document.getElementById('compare-btn-' + id);
        if (btn) btn.classList.add('text-green-600');
    }

    saveCompareList(list);
    updateCompareUI();
}

function clearCompare() {
    saveCompareList([]);
    updateCompareUI();

    // Remove highlights
    document.querySelectorAll('[id^="compare-btn-"]').forEach(function (btn) {
        btn.classList.remove('text-green-600');
    });
}

function updateCompareUI() {
    const list = getCompareList();
    const bar = document.getElementById('compare-bar');
    const navBtn = document.getElementById('compare-nav-btn');
    const countEl = document.getElementById('compare-count');
    const itemsEl = document.getElementById('compare-items');
    const goBtn = document.getElementById('compare-go-btn');

    if (!bar) return;

    if (list.length > 0) {
        bar.classList.remove('hidden');
        if (navBtn) navBtn.classList.remove('hidden');
    } else {
        bar.classList.add('hidden');
        if (navBtn) navBtn.classList.add('hidden');
    }

    if (countEl) countEl.textContent = list.length;

    if (itemsEl) {
        itemsEl.innerHTML = list.map(function (item) {
            return '<div class="flex items-center gap-1.5 bg-gray-100 dark:bg-gray-700 rounded-lg px-3 py-1.5">' +
                '<span class="text-sm font-medium text-gray-800 dark:text-gray-200 max-w-[120px] truncate">' + item.name + '</span>' +
                '<button onclick="toggleCompare(' + item.id + ', \'' + item.name.replace(/'/g, "\\'") + '\')" class="text-gray-400 hover:text-red-500 ml-1">' +
                '<svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>' +
                '</button>' +
                '</div>';
        }).join('');
    }

    if (goBtn) {
        const ids = list.map(function (i) { return 'id=' + i.id; }).join('&');
        goBtn.href = '/so-sanh?' + ids;
    }
}

// Auto-redirect compare page from localStorage if no URL params
(function () {
    if (window.location.pathname === '/so-sanh') {
        const params = new URLSearchParams(window.location.search);
        const ids = params.getAll('id');
        if (ids.length === 0) {
            // Opened without URL params (e.g. nav link) — redirect using localStorage
            try {
                const list = JSON.parse(localStorage.getItem('compareList') || '[]');
                if (list.length > 0) {
                    const qs = list.map(function (i) { return 'id=' + i.id; }).join('&');
                    window.location.replace('/so-sanh?' + qs);
                }
            } catch (e) {}
        }
    }
})();
