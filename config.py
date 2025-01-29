import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Lấy các biến môi trường
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USER_TAG = os.getenv("USER_TAG", "")

# Các hằng số / đường dẫn cố định
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
URL = "https://www.24h.com.vn/gia-vang-hom-nay-c425.html"
TIMEOUT = 15
