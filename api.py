from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from db_manager import get_voting_status, check_and_vote
import os

# Flask с указанием папки со статикой
app = Flask(__name__, static_folder="web_app", static_url_path="/web_app")
CORS(app)

# -----------------------------
# API для Web App
# -----------------------------
@app.route('/api/status', methods=['GET'])
def get_status():
    """Возвращает статус всех голосований и таймеры."""
    return jsonify(get_voting_status())

@app.route('/api/vote', methods=['POST'])
def handle_vote():
    """Принимает голос от Web App."""
    data = request.json
    user_id = data.get('user_id')
    phase_id = data.get('phase_id')
    country = data.get('country')
    
    if not all([user_id, phase_id, country]):
        return jsonify({"success": False, "message": "Недостаточно данных."}), 400

    success, message = check_and_vote(user_id, phase_id, country)
    return jsonify({"success": success, "message": message})

# -----------------------------
# Раздача Web App (HTML, JS, CSS)
# -----------------------------
@app.route('/web_app/<path:path>')
def serve_web_app(path):
    """Отдаёт статические файлы Web App (JS, CSS)."""
    return send_from_directory('web_app', path)

@app.route('/')
def index():
    """Главная страница — Web App index.html."""
    return send_from_directory('web_app', 'index.html')

# -----------------------------
# Запуск
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
