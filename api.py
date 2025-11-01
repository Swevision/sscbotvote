from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from db_manager import get_voting_status, check_and_vote
import os

# === Конфигурация ===
app = Flask(__name__, static_folder="web_app")
CORS(app)

# 🔗 URL твоего WebApp (можешь поменять, когда задеплоишь)
RENDER_URL = "https://swevision-vote.onrender.com"
WEB_APP_URL = f"{RENDER_URL}/web_app/index.html"

# 🔐 Токен бота (можешь хранить в Render → Environment)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7443232882:AAHpg-07k7xXeiJeBOErXklGBByoJ7IoTuc")


# ==========================
# 🌐 API endpoints
# ==========================

@app.route('/api/status', methods=['GET'])
def get_status():
    """Возвращает статус всех голосований"""
    return jsonify(get_voting_status())


@app.route('/api/vote', methods=['POST'])
def handle_vote():
    """Принимает голос от WebApp"""
    data = request.json or {}

    user_id = data.get('user_id')
    phase_id = data.get('phase_id')
    country = data.get('country')
    init_data = data.get('initData')  # для проверки Telegram (опционально)

    if not all([user_id, phase_id, country]):
        return jsonify({"success": False, "message": "Недостаточно данных."}), 400

    success, message = check_and_vote(user_id, phase_id, country)
    return jsonify({"success": success, "message": message})


# ==========================
# 🧩 WebApp (Frontend)
# ==========================

@app.route('/')
def root():
    """Редиректим на главную страницу WebApp"""
    return send_from_directory('web_app', 'index.html')


@app.route('/web_app/<path:path>')
def send_web_app(path):
    """Отдаём статические файлы WebApp (HTML, CSS, JS)"""
    return send_from_directory('web_app', path)


# ==========================
# 🚀 Запуск (локальный)
# ==========================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Запуск Flask API на порту {port}...")
    app.run(host='0.0.0.0', port=port)