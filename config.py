import os

ESP32_URL = os.getenv("ESP32_URL", "http://192.168.1.50/open")
ESP32_KEY = os.getenv("ESP32_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_IDS = [
    chat_id.strip()
    for chat_id in os.getenv("TELEGRAM_CHAT_IDS", "").split(",")
    if chat_id.strip()
]
THRESHOLD = float(os.getenv("THRESHOLD", "0.50"))
MAX_FAILS = int(os.getenv("MAX_FAILS", "3"))
ENROLL_PIN = os.getenv("ENROLL_PIN", "")