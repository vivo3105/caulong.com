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

    // ─── Nav Search Autocomplete ──────────────────────────────────────────────

    const navSearch = document.getElementById('nav-search');
    const searchResults = document.getElementById('search-results');
    const searchClear = document.getElementById('search-clear');

    if (navSearch && searchResults) {
        let searchTimeout = null;
        let activeIndex = -1;
        let suggestions = [];
        let origValue = '';
        let currentQ = '';

        // Inject animation style once
        if (!document.getElementById('search-anim-style')) {
            var st = document.createElement('style');
            st.id = 'search-anim-style';
            st.textContent =
                '#search-results{transition:opacity .15s ease,transform .15s ease;transform-origin:top center}' +
                '#search-results.hidden{opacity:0;transform:scaleY(.96);pointer-events:none}' +
                '#search-results:not(.hidden){opacity:1;transform:scaleY(1)}' +
                '@keyframes shimmer{0%{background-position:-400px 0}100%{background-position:400px 0}}' +
                '.skeleton{background:linear-gradient(90deg,#f0f0f0 25%,#e0e0e0 50%,#f0f0f0 75%);background-size:400px 100%;animation:shimmer 1.2s infinite}' +
                '.dark .skeleton{background:linear-gradient(90deg,#374151 25%,#4b5563 50%,#374151 75%);background-size:400px 100%}' +
                '.suggest-item.active{background:rgba(16,185,129,.08)}' +
                '.dark .suggest-item.active{background:rgba(16,185,129,.12)}';
            document.head.appendChild(st);
        }

        function esc(s) {
            return String(s)
                .replace(/&/g, '&amp;').replace(/</g, '&lt;')
                .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }

        function highlight(text, q) {
            if (!q) return esc(text);
            var re = new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
            return esc(text).replace(re, '<mark class="bg-transparent text-green-600 dark:text-green-400 font-semibold not-italic">$1</mark>');
        }

        function showDropdown() {
            searchResults.classList.remove('hidden');
        }

        function closeDropdown() {
            searchResults.classList.add('hidden');
            activeIndex = -1;
            suggestions = [];
        }

        function showSkeleton() {
            var rows = '';
            for (var i = 0; i < 3; i++) {
                rows += '<div class="flex items-center gap-3 px-4 py-3">' +
                    '<div class="skeleton w-4 h-4 rounded flex-shrink-0"></div>' +
                    '<div class="flex-1 space-y-1.5">' +
                    '<div class="skeleton h-3.5 rounded w-3/4"></div>' +
                    '<div class="skeleton h-2.5 rounded w-1/3"></div>' +
                    '</div></div>';
            }
            searchResults.innerHTML = rows;
            showDropdown();
        }

        function renderSuggestions(data, q) {
            activeIndex = -1;
            suggestions = data;

            if (data.length === 0) {
                searchResults.innerHTML =
                    '<div class="px-4 py-4 text-sm text-gray-400 dark:text-gray-500 flex items-center gap-2">' +
                    '<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">' +
                    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>' +
                    'Không tìm thấy "<em class="text-gray-500 dark:text-gray-400">' + esc(q) + '</em>"</div>';
                showDropdown();
                return;
            }

            var html = data.map(function (item, i) {
                return '<div role="option" data-idx="' + i + '" data-slug="' + esc(item.slug) + '"' +
                    ' class="suggest-item flex items-center gap-3 px-4 py-2.5 cursor-pointer transition-colors select-none">' +
                    '<svg class="w-4 h-4 flex-shrink-0 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">' +
                    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>' +
                    '<div class="flex-1 min-w-0">' +
                    '<p class="text-sm text-gray-900 dark:text-gray-100 truncate leading-snug">' + highlight(item.name, q) + '</p>' +
                    '<p class="text-xs text-gray-400 dark:text-gray-500 truncate">' + esc(item.brand) + '</p>' +
                    '</div>' +
                    '<svg class="w-3.5 h-3.5 flex-shrink-0 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">' +
                    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 17L17 7M7 7h10v10"/></svg>' +
                    '</div>';
            }).join('');

            html += '<a href="/search?q=' + encodeURIComponent(q) + '"' +
                ' class="flex items-center justify-between gap-2 px-4 py-2.5 border-t border-gray-100 dark:border-gray-700' +
                ' hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors group">' +
                '<span class="text-sm text-green-600 dark:text-green-400 font-medium truncate">' +
                'Xem tất cả "<span class="font-semibold">' + esc(q) + '</span>"</span>' +
                '<svg class="w-4 h-4 flex-shrink-0 text-green-500 dark:text-green-400 transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">' +
                '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>' +
                '</a>';

            searchResults.innerHTML = html;
            showDropdown();

            searchResults.querySelectorAll('.suggest-item').forEach(function (el) {
                el.addEventListener('mousedown', function (e) {
                    e.preventDefault();
                    window.location.href = '/vot-cau-long/' + el.dataset.slug;
                });
                el.addEventListener('mouseenter', function () {
                    searchResults.querySelectorAll('.suggest-item').forEach(function (x) { x.classList.remove('active'); });
                    el.classList.add('active');
                    activeIndex = parseInt(el.dataset.idx);
                });
                el.addEventListener('mouseleave', function () {
                    el.classList.remove('active');
                });
            });
        }

        function setActive(idx) {
            var items = searchResults.querySelectorAll('.suggest-item');
            items.forEach(function (el) { el.classList.remove('active'); });
            activeIndex = idx;
            if (idx >= 0 && idx < items.length) {
                items[idx].classList.add('active');
                navSearch.value = suggestions[idx].name;
            } else {
                navSearch.value = origValue;
            }
        }

        navSearch.addEventListener('input', function () {
            var q = this.value.trim();
            origValue = this.value;
            activeIndex = -1;
            currentQ = q;
            if (searchClear) searchClear.classList.toggle('hidden', q.length === 0);
            clearTimeout(searchTimeout);
            if (q.length < 1) { closeDropdown(); return; }

            showSkeleton();

            searchTimeout = setTimeout(function () {
                var fetchQ = q;
                fetch('/suggest?q=' + encodeURIComponent(fetchQ))
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (fetchQ === currentQ) renderSuggestions(data, fetchQ);
                    })
                    .catch(function () { if (fetchQ === currentQ) closeDropdown(); });
            }, 220);
        });

        navSearch.addEventListener('keydown', function (e) {
            var items = searchResults.querySelectorAll('.suggest-item');
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                setActive(Math.min(activeIndex + 1, items.length - 1));
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                setActive(activeIndex <= 0 ? -1 : activeIndex - 1);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (activeIndex >= 0 && suggestions[activeIndex]) {
                    window.location.href = '/vot-cau-long/' + suggestions[activeIndex].slug;
                } else {
                    var q = navSearch.value.trim();
                    if (q) window.location.href = '/search?q=' + encodeURIComponent(q);
                }
            } else if (e.key === 'Escape') {
                closeDropdown();
                navSearch.blur();
            }
        });

        if (searchClear) {
            searchClear.addEventListener('click', function () {
                navSearch.value = '';
                origValue = '';
                currentQ = '';
                searchClear.classList.add('hidden');
                closeDropdown();
                navSearch.focus();
            });
        }

        document.addEventListener('click', function (e) {
            if (!e.target.closest('#search-wrapper')) closeDropdown();
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
