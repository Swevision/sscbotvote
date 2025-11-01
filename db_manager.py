import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'voting_data.db'
VOTING_PHASES = {
    "first_semi": {"start": "2026-05-12 20:00:00", "end": "2026-05-12 22:00:00",
                   "countries": ["Aland", "Belgium", "Cyprus", "Denmark"]},
    "second_semi": {"start": "2026-05-14 20:00:00", "end": "2026-05-14 22:00:00",
                    "countries": ["Estonia", "Finland", "Germany", "Greece"]},
    "grand_final": {"start": "2026-05-16 20:00:00", "end": "2026-05-16 23:00:00",
                    "countries": ["Iceland", "Ireland", "Italy", "Norway"]},
}


def init_db():
    """Инициализация таблиц для хранения голосов."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            phase_id TEXT NOT NULL,
            country TEXT NOT NULL,
            voted_at TEXT NOT NULL,
            UNIQUE(user_id, phase_id)
        )
    """)
    conn.commit()
    conn.close()


def get_voting_status():
    """Получение статуса голосований с оставшимся временем."""
    statuses = {}
    now = datetime.now()
    for phase_id, phase_data in VOTING_PHASES.items():
        start = datetime.strptime(phase_data['start'], "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(phase_data['end'], "%Y-%m-%d %H:%M:%S")

        if now < start:
            # Не началось
            remaining = start - now
            status = {"active": False, "status": f"Начнется через {str(remaining).split('.')[0]}", "countries": []}
        elif start <= now <= end:
            # Активно
            remaining = end - now
            status = {"active": True, "status": f"До конца голосования осталось {str(remaining).split('.')[0]}",
                      "countries": phase_data['countries']}
        else:
            # Закончилось
            status = {"active": False, "status": "Голосование завершено", "countries": []}

        statuses[phase_id] = status
    return statuses


def check_and_vote(user_id, phase_id, country):
    """Проверка, голосовал ли пользователь, и запись голоса."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Проверка, голосовал ли уже
    cursor.execute("SELECT 1 FROM votes WHERE user_id=? AND phase_id=?", (user_id, phase_id))
    if cursor.fetchone():
        conn.close()
        return False, "Вы уже проголосовали за этот этап."

    # 2. Проверка, активно ли голосование
    status = get_voting_status().get(phase_id)
    if not status or not status['active']:
        conn.close()
        return False, "Голосование в данный момент не доступно."

    # 3. Запись голоса
    try:
        voted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO votes (user_id, phase_id, country, voted_at) VALUES (?, ?, ?, ?)",
                       (user_id, phase_id, country, voted_at))
        conn.commit()
        conn.close()
        return True, "Ваш голос успешно учтен!"
    except Exception as e:
        conn.close()
        return False, f"Ошибка при записи голоса: {e}"


init_db()