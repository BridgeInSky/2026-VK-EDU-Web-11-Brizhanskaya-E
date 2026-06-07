// Полнотекстовый поиск с debounce
let searchTimeout;
let currentQuery = '';

const searchInput = document.getElementById('search-input');
const suggestionsDiv = document.getElementById('search-suggestions');

if (searchInput) {
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        currentQuery = query;
        
        // Очищаем предыдущий таймаут
        clearTimeout(searchTimeout);
        
        // Скрываем подсказки, если запрос слишком короткий
        if (query.length < 2) {
            suggestionsDiv.style.display = 'none';
            return;
        }
        
        // Устанавливаем задержку 300ms (debounce)
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
    
    // Обработка клавиш
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            suggestionsDiv.style.display = 'none';
            searchInput.blur();
        }
    });
    
    // Закрытие подсказок при потере фокуса
    searchInput.addEventListener('blur', function() {
        // Даем время на клик по ссылке
        setTimeout(() => {
            if (!suggestionsDiv.matches(':hover')) {
                suggestionsDiv.style.display = 'none';
            }
        }, 200);
    });
}

function performSearch(query) {
    if (query !== currentQuery) return;
    
    fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (query !== currentQuery) return;
            showSuggestions(data.results);
        })
        .catch(error => {
            console.error('Search error:', error);
            showError('Ошибка при выполнении поиска');
        });
}

function showSuggestions(results) {
    if (results.length === 0) {
        suggestionsDiv.style.display = 'none';
        return;
    }
    
    const html = results.map(result => `
        <a href="/question/${result.id}/" 
           class="search-suggestion-item d-block p-3 text-decoration-none border-bottom hover-bg-light"
           style="transition: background-color 0.2s;">
            <div class="fw-bold text-dark">${escapeHtml(result.title)}</div>
            <div class="small text-muted mt-1">${escapeHtml(result.preview)}</div>
            <div class="small text-primary mt-1">Перейти к вопросу →</div>
        </a>
    `).join('');
    
    suggestionsDiv.innerHTML = `
        <div class="search-suggestions-header p-2 bg-light border-bottom">
            <small class="text-muted">Найдено ${results.length} вопросов</small>
        </div>
        ${html}
    `;
    
    suggestionsDiv.style.display = 'block';
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    errorDiv.style.zIndex = '9999';
    errorDiv.innerHTML = `
        ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// // Добавляем стили для подсказок
// const style = document.createElement('style');
// style.textContent = `
//     #search-suggestions {
//         max-height: 400px;
//         overflow-y: auto;
//         box-shadow: 0 4px 12px rgba(0,0,0,0.15);
//         border-radius: 8px;
//         margin-top: 5px;
//     }
//     .search-suggestion-item:hover {
//         background-color: #f8f9fa !important;
//     }
//     .search-suggestion-item:active {
//         background-color: #e9ecef !important;
//     }
// `;
// document.head.appendChild(style);

// Закрытие подсказок при клике вне
document.addEventListener('click', function(e) {
    if (!e.target.closest('#search-input') && !e.target.closest('#search-suggestions')) {
        if (suggestionsDiv) {
            suggestionsDiv.style.display = 'none';
        }
    }
});