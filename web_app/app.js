const API_BASE_URL = 'https://your-render-app-name.onrender.com/api'; // ЗАМЕНИТЕ НА ВАШ URL
const user_id = new URLSearchParams(window.location.search).get('user_id'); // Получаем ID из URL бота

let currentLanguage = 'rus';
let currentPhaseId = null;

// Инициализация Web App SDK
Telegram.WebApp.ready();
Telegram.WebApp.expand();
// Включаем виброотклик
Telegram.WebApp.HapticFeedback.impactOccurred('light');

// --- Управление Экранами ---
function switchScreen(targetId) {
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => {
        if (screen.id === targetId) {
            screen.classList.remove('fade-out');
            screen.classList.add('active', 'fade-in');
            screen.style.display = 'block';
        } else {
            screen.classList.remove('active', 'fade-in');
            screen.classList.add('fade-out');
            setTimeout(() => screen.style.display = 'none', 500); // Задержка для анимации
        }
    });
}

// --- Кнопка "Назад" ---
Telegram.WebApp.BackButton.onClick(() => {
    if (document.getElementById('voting-screen').classList.contains('active')) {
        // Выход с экрана голосования на экран этапов
        switchScreen('phase-screen');
        Telegram.WebApp.BackButton.show(); // Если нужно подтверждение, используйте showConfirm
        Telegram.WebApp.MainButton.hide();
        currentPhaseId = null;
    } else if (document.getElementById('phase-screen').classList.contains('active')) {
        // Выход с экрана этапов на экран языка
        switchScreen('language-screen');
    } else {
        // Закрытие Web App
        Telegram.WebApp.close();
    }
});
Telegram.WebApp.BackButton.show();


// --- 1. Экран Языка ---
document.querySelectorAll('.lang-selector button').forEach(button => {
    button.addEventListener('click', (e) => {
        currentLanguage = e.target.getAttribute('data-lang');
        fetchVotingStatus();
        switchScreen('phase-screen');
    });
});

// --- 2. Экран Этапов ---
async function fetchVotingStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/status`);
        const statuses = await response.json();
        renderPhaseScreen(statuses);
    } catch (error) {
        Telegram.WebApp.showAlert('Не удалось загрузить статус голосований. Попробуйте позже.');
        console.error('Fetch error:', error);
    }
}

function renderPhaseScreen(statuses) {
    const phaseList = document.getElementById('phase-list');
    phaseList.innerHTML = '';

    // Переводы (для MVP просто заменяем)
    const titles = {
        "first_semi": "First Semi-Final",
        "second_semi": "Second Semi-Final",
        "grand_final": "Grand Final"
    };

    for (const [id, data] of Object.entries(statuses)) {
        const card = document.createElement('div');
        card.className = `phase-card ${data.active ? 'active-vote' : 'inactive-vote'}`;
        card.setAttribute('data-id', id);

        card.innerHTML = `
            <h3>${titles[id] || id}</h3>
            <p class="phase-status">${data.status}</p>
        `;

        card.addEventListener('click', () => handlePhaseClick(id, data));
        phaseList.appendChild(card);
    }

    // Обновляем таймеры каждую секунду
    setInterval(fetchVotingStatus, 1000);
}

function handlePhaseClick(id, data) {
    currentPhaseId = id;

    // Проверка, что пользователь уже голосовал (нужно получать из API)
    // Для MVP, простая проверка статуса:
    if (data.status.includes('Вы уже проголосовали')) {
        Telegram.WebApp.showAlert('Вы уже проголосовали за этот этап!');
        return;
    }

    if (!data.active) {
        Telegram.WebApp.showAlert('Голосование в данный момент не доступно. ' + data.status);
        return;
    }

    // Активация кнопки "VOTE NOW!" и переход к голосованию
    renderVotingScreen(id, data);
    switchScreen('voting-screen');
}


// --- 3. Экран Голосования ---
let selectedCountry = null;

function renderVotingScreen(phaseId, data) {
    const countryList = document.getElementById('countries-list');
    countryList.innerHTML = '';
    selectedCountry = null;

    // Обновляем таймер в заголовке
    document.getElementById('voting-timer').textContent = data.status;

    data.countries.forEach(country => {
        const item = document.createElement('div');
        item.className = 'country-item';
        item.textContent = country;
        item.setAttribute('data-country', country);

        item.addEventListener('click', () => {
            document.querySelectorAll('.country-item').forEach(c => c.classList.remove('selected'));
            item.classList.add('selected');
            selectedCountry = country;
            Telegram.WebApp.MainButton.setText('VOTE NOW!');
            Telegram.WebApp.MainButton.show();
        });
        countryList.appendChild(item);
    });

    // Настройка Главной Кнопки ТГ
    Telegram.WebApp.MainButton.setParams({
        text: 'Выберите страну',
        color: Telegram.WebApp.themeParams.button_color || '#50a8eb',
        text_color: Telegram.WebApp.themeParams.button_text_color || '#ffffff',
        is_visible: false,
        is_active: true
    });

    // Назначаем обработчик для кнопки
    Telegram.WebApp.MainButton.onClick(submitVote);
}

async function submitVote() {
    if (!selectedCountry) {
        Telegram.WebApp.showAlert('Пожалуйста, выберите страну.');
        return;
    }

    // 1. Блокируем кнопку
    Telegram.WebApp.MainButton.showProgress();

    try {
        const response = await fetch(`${API_BASE_URL}/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: user_id,
                phase_id: currentPhaseId,
                country: selectedCountry,
                initData: Telegram.WebApp.initData // Отправляем для проверки
            })
        });

        const result = await response.json();

        Telegram.WebApp.MainButton.hideProgress();

        if (result.success) {
            Telegram.WebApp.showPopup({
                title: 'Успех! 🗳️',
                message: result.message,
                buttons: [{ id: 'ok', type: 'default', text: 'Готово' }]
            }, () => {
                // Переходим на главный экран и обновляем статус
                Telegram.WebApp.MainButton.hide();
                switchScreen('phase-screen');
                fetchVotingStatus();
            });
        } else {
            Telegram.WebApp.showAlert(result.message);
        }
    } catch (error) {
        Telegram.WebApp.MainButton.hideProgress();
        Telegram.WebApp.showAlert('Произошла ошибка сети. Попробуйте снова.');
        console.error('Vote error:', error);
    }
}

// Запуск при загрузке
document.addEventListener('DOMContentLoaded', () => {
    // Начало с экрана выбора языка
    // Если пользователь уже выбрал язык, можно добавить логику сохранения в localStorage
});