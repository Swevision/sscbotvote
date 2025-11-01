import os
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN") or "7443232882:AAHpg-07k7xXeiJeBOErXklGBByoJ7IoTuc"
WEBHOOK_URL = "https://my-vote-app.onrender.com/webhook"  # Render URL + путь webhook

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
resp = requests.get(url, params={"url": WEBHOOK_URL})
print(resp.json())
