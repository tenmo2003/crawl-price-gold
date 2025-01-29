import requests
from config import TELEGRAM_URL, CHAT_ID, TIMEOUT

def send_to_telegram(message, parse_mode="MarkdownV2"):
    """
    Gửi tin nhắn đến Telegram bằng Bot.
    """
    print("Sending message to Telegram...")
    try:
        response = requests.post(
            TELEGRAM_URL,
            data={
                'chat_id': CHAT_ID,
                'text': message,
                'parse_mode': parse_mode
            },
            timeout=TIMEOUT
        )
        if response.status_code != 200:
            print(f"Error sending message: {response.status_code}, {response.text}")
        else:
            print("Message sent successfully.")
    except requests.RequestException as e:
        print(f"Error sending message to Telegram: {e}")
