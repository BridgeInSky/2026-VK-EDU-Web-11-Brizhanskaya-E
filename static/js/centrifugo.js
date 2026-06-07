// Подключение к Centrifugo для real-time уведомлений
let centrifuge = null;
let currentQuestionId = null;

function initCentrifugo(questionId) {
    currentQuestionId = questionId;
    console.log('Initializing Centrifugo for question:', questionId);
    connectCentrifugo();
}

function connectCentrifugo() {
    const wsUrl = 'ws://localhost:8001/connection/websocket';
    console.log('Connecting to Centrifugo at:', wsUrl);
    
    centrifuge = new Centrifuge(wsUrl);
    
    centrifuge.on('connecting', function(ctx) {
        console.log('Centrifugo connecting...');
    });
    
    centrifuge.on('connected', function(ctx) {
        console.log('✅ Connected to Centrifugo!');
        
        const channel = `questions:${currentQuestionId}`;
        console.log('Subscribing to channel:', channel);
        
        const sub = centrifuge.newSubscription(channel);
        
        sub.on('publication', function(ctx) {
            console.log('📨 New answer received:', ctx.data);
            handleNewAnswer(ctx.data);
        });
        
        sub.on('subscribed', function() {
            console.log('✅ Subscribed to channel:', channel);
        });
        
        sub.on('error', function(ctx) {
            console.error('Subscription error:', ctx);
        });
        
        sub.subscribe();
    });
    
    centrifuge.on('disconnected', function(ctx) {
        console.log('Disconnected from Centrifugo');
    });
    
    centrifuge.on('error', function(ctx) {
        console.error('Centrifugo error:', ctx);
    });
    
    centrifuge.connect();
}

function handleNewAnswer(data) {
    console.log('New answer data:', data);
    
    // Проверяем, что это ответ (есть answer_id)
    if (!data.answer_id) {
        console.log('Not an answer notification, skipping:', data);
        return;
    }
    
    const currentPage = getCurrentPage();
    
    if (currentPage === 1) {
        addAnswerToPage(data);
    } else {
        showNewAnswerAlert(data);
    }
}

function getCurrentPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = parseInt(urlParams.get('page'));
    return isNaN(page) ? 1 : page;
}

function addAnswerToPage(data) {
    const answersList = document.querySelector('.answers-list');
    if (!answersList) return;
    
    const emptyAlert = answersList.querySelector('.alert-info');
    if (emptyAlert && emptyAlert.classList.contains('alert-info')) {
        emptyAlert.remove();
    }
    
    const existingAnswer = document.getElementById(`answer-${data.answer_id}`);
    if (existingAnswer) {
        console.log('Answer already exists');
        return;
    }
    
    const newAnswerHtml = createAnswerElement(data);
    answersList.insertAdjacentHTML('afterbegin', newAnswerHtml);
    updateAnswersCount();
    showToastNotification(data);
    
    // Прокручиваем к новому ответу
    const newAnswer = document.getElementById(`answer-${data.answer_id}`);
    if (newAnswer) {
        newAnswer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function createAnswerElement(data) {
    const avatarUrl = '/static/img/avatars/avatar-default.png';
    const answerText = data.answer_preview || data.text || 'Новый ответ';
    
    return `
        <div class="card mb-3 new-answer" id="answer-${data.answer_id}" style="animation: highlight 2s ease-out;">
            <div class="card-body">
                <div class="row">
                    <div class="col-auto">
                        <div class="vote-widget answer-vote text-center" data-answer-id="${data.answer_id}">
                            <button class="btn btn-sm btn-outline-success vote-btn like">▲</button>
                            <div class="vote-count fw-bold my-1">0</div>
                            <button class="btn btn-sm btn-outline-danger vote-btn dislike">▼</button>
                        </div>
                    </div>
                    <div class="col">
                        <p class="card-text">${escapeHtml(answerText)}</p>
                        <div class="text-muted small">
                            <img src="${avatarUrl}" class="rounded-circle" width="24" height="24" style="object-fit: cover;">
                            ${escapeHtml(data.author)} | только что
                            <span class="badge bg-success ms-2">Новый!</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function showNewAnswerAlert(data) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-info alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '350px';
    alertDiv.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    alertDiv.innerHTML = `
        <strong>📢 Новый ответ!</strong><br>
        ${escapeHtml(data.author)} ответил(а) на этот вопрос.
        <hr class="my-2">
        <button class="btn btn-sm btn-primary me-2" onclick="window.location.href='?page=1#answer-${data.answer_id}'">
            Перейти к ответу
        </button>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.appendChild(alertDiv);
    setTimeout(() => {
        if (alertDiv && alertDiv.parentNode) alertDiv.remove();
    }, 8000);
}

function showToastNotification(data) {
    // Проверяем, что есть нужные поля
    if (!data || !data.author) {
        console.log('Invalid notification data:', data);
        return;
    }
    
    const answerPreview = data.answer_preview || data.text || 'Новый ответ';
    const previewText = answerPreview.length > 80 ? answerPreview.substring(0, 80) + '...' : answerPreview;
    
    const toast = document.createElement('div');
    toast.className = 'position-fixed bottom-0 end-0 m-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="toast show" role="alert" data-bs-autohide="true" data-bs-delay="4000">
            <div class="toast-header bg-success text-white">
                <strong class="me-auto">📬 Новый ответ</strong>
                <small>только что</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                <strong>${escapeHtml(data.author)}</strong> ответил(а):<br>
                "${escapeHtml(previewText)}"
            </div>
        </div>
    `;
    document.body.appendChild(toast);
    
    // Инициализируем Bootstrap Toast
    const toastElement = toast.querySelector('.toast');
    if (typeof bootstrap !== 'undefined') {
        const bsToast = new bootstrap.Toast(toastElement, { delay: 4000 });
        bsToast.show();
    }
    
    // Удаляем из DOM после скрытия
    setTimeout(() => {
        if (toast && toast.parentNode) toast.remove();
    }, 4000);
}

function updateAnswersCount() {
    const answersHeader = document.getElementById('answers-count-header');
    if (answersHeader) {
        const match = answersHeader.textContent.match(/\d+/);
        if (match) {
            const currentCount = parseInt(match[0]);
            const newCount = currentCount + 1;
            answersHeader.innerHTML = answersHeader.innerHTML.replace(currentCount, newCount);
        }
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Добавляем CSS анимацию для новых ответов
const style = document.createElement('style');
style.textContent = `
    @keyframes highlight {
        0% { background-color: rgba(40, 167, 69, 0.3); }
        100% { background-color: transparent; }
    }
    .new-answer {
        animation: highlight 2s ease-out;
    }
    .toast {
        opacity: 1 !important;
    }
`;
document.head.appendChild(style);

// Инициализация на странице вопроса
document.addEventListener('DOMContentLoaded', function() {
    const questionCard = document.querySelector('[data-question-id]');
    if (questionCard) {
        const questionId = questionCard.dataset.questionId;
        if (questionId) {
            initCentrifugo(questionId);
        }
    }
});