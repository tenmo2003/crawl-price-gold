import requests
from config import BOT_TOKEN, TELEGRAM_URL, CHAT_ID, TIMEOUT

def send_to_telegram(message, chat_id=None, parse_mode="MarkdownV2"):
    """
    Gửi tin nhắn đến Telegram bằng Bot.
    """
    print("Sending message to Telegram...")
    effective_chat_id = chat_id or CHAT_ID
    if not effective_chat_id:
        print("CHAT_ID is missing; cannot send Telegram message.")
        return False

    try:
        response = requests.post(
            TELEGRAM_URL,
            data={
                'chat_id': effective_chat_id,
                'text': message,
                'parse_mode': parse_mode
            },
            timeout=TIMEOUT
        )
        if response.status_code != 200:
            print(f"Error sending message: {response.status_code}, {response.text}")
            return False
        else:
            print("Message sent successfully.")
            return True
    except requests.RequestException as e:
        print(f"Error sending message to Telegram: {e}")
        return False


def get_updates(offset=None, timeout=0, limit=100):
    if not BOT_TOKEN:
        print("BOT_TOKEN is missing; cannot fetch Telegram updates.")
        return []

    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": timeout, "limit": limit}
    if offset is not None:
        params["offset"] = offset

    try:
        response = requests.get(base_url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            print(f"Telegram getUpdates failed: {payload}")
            return []
        return payload.get("result", [])
    except requests.RequestException as e:
        print(f"Error fetching Telegram updates: {e}")
        return []
