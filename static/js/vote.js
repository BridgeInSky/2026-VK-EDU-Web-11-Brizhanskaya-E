// CSRF Token для AJAX запросов
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Обработка лайков вопросов
function handleQuestionLike(questionId, button, action) {
    console.log('Sending question like:', questionId, action);
    
    fetch(`/api/question-like/${questionId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: action })
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 403) {
                window.location.href = '/login/?next=' + window.location.pathname;
                return;
            }
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            showError(data.error);
            return;
        }
        
        const voteCount = button.closest('.vote-widget').querySelector('.vote-count');
        voteCount.textContent = data.new_rating;
        
        const likeBtn = button.closest('.vote-widget').querySelector('.like');
        const dislikeBtn = button.closest('.vote-widget').querySelector('.dislike');
        
        if (data.user_vote === 1) {
            likeBtn.classList.add('btn-success');
            likeBtn.classList.remove('btn-outline-success');
            dislikeBtn.classList.remove('btn-danger');
            dislikeBtn.classList.add('btn-outline-danger');
        } else if (data.user_vote === -1) {
            dislikeBtn.classList.add('btn-danger');
            dislikeBtn.classList.remove('btn-outline-danger');
            likeBtn.classList.remove('btn-success');
            likeBtn.classList.add('btn-outline-success');
        } else {
            likeBtn.classList.remove('btn-success');
            likeBtn.classList.add('btn-outline-success');
            dislikeBtn.classList.remove('btn-danger');
            dislikeBtn.classList.add('btn-outline-danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Произошла ошибка при голосовании');
    });
}

// Обработка лайков ответов
function handleAnswerLike(answerId, button, action) {
    console.log('Sending answer like:', answerId, action);
    
    fetch(`/api/answer-like/${answerId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: action })
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 403) {
                window.location.href = '/login/?next=' + window.location.pathname;
                return;
            }
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            showError(data.error);
            return;
        }
        
        const voteCount = button.closest('.vote-widget').querySelector('.vote-count');
        voteCount.textContent = data.new_rating;
        
        const likeBtn = button.closest('.vote-widget').querySelector('.like');
        const dislikeBtn = button.closest('.vote-widget').querySelector('.dislike');
        
        if (data.user_vote === 1) {
            likeBtn.classList.add('btn-success');
            likeBtn.classList.remove('btn-outline-success');
            dislikeBtn.classList.remove('btn-danger');
            dislikeBtn.classList.add('btn-outline-danger');
        } else if (data.user_vote === -1) {
            dislikeBtn.classList.add('btn-danger');
            dislikeBtn.classList.remove('btn-outline-danger');
            likeBtn.classList.remove('btn-success');
            likeBtn.classList.add('btn-outline-success');
        } else {
            likeBtn.classList.remove('btn-success');
            likeBtn.classList.add('btn-outline-success');
            dislikeBtn.classList.remove('btn-danger');
            dislikeBtn.classList.add('btn-outline-danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Произошла ошибка при голосовании');
    });
}

// Отметка правильного ответа
function markAsCorrect(answerId, button) {
    fetch(`/api/mark-correct/${answerId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showError(data.error);
            return;
        }
        
        if (data.is_correct) {
            button.textContent = '✓ Правильный';
            button.classList.remove('btn-outline-success');
            button.classList.add('btn-success');
            
            document.querySelectorAll('.mark-correct-btn').forEach(btn => {
                if (btn !== button) {
                    btn.textContent = 'Отметить';
                    btn.classList.remove('btn-success');
                    btn.classList.add('btn-outline-success');
                }
            });
        } else {
            button.textContent = 'Отметить';
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Произошла ошибка');
    });
}

function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 3000);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log("vote.js загружен!");
    
    // Обработка лайков вопросов
    document.querySelectorAll('.question-vote .like, .question-vote .dislike').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const card = this.closest('[data-question-id]');
            const questionId = card?.dataset.questionId;
            const action = this.classList.contains('like') ? 'like' : 'dislike';
            if (questionId) handleQuestionLike(questionId, this, action);
        });
    });
    
    // Обработка лайков ответов
    document.querySelectorAll('.answer-vote .like, .answer-vote .dislike').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const card = this.closest('[data-answer-id]');
            const answerId = card?.dataset.answerId;
            const action = this.classList.contains('like') ? 'like' : 'dislike';
            if (answerId) handleAnswerLike(answerId, this, action);
        });
    });
    
    // Обработка отметки правильного ответа
    document.querySelectorAll('.mark-correct-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const answerId = this.dataset.answerId;
            if (answerId) markAsCorrect(answerId, this);
        });
    });
});