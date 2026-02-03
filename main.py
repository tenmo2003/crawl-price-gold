from datetime import datetime, timedelta, timezone
import argparse
import json
import os

from services.fetcher import (
    fetch_btmc_gold_prices,
    fetch_domestic_gold_prices,
    fetch_international_gold_prices,
)
from services.formatter import format_btmc_data, format_domestic_data, format_international_data
from services.telegram_bot import get_updates, send_to_telegram
from utils.day_converter import convert_day_to_vietnamese


AVAILABLE_TYPES = ["domestic", "international", "btmc"]


def _state_dir():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_dir, ".state")


def _updates_state_path():
    return os.path.join(_state_dir(), "telegram_offset.json")


def _load_update_offset(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        value = state.get("last_update_id")
        return value if isinstance(value, int) else None
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Failed to load update offset: {e}")
        return None


def _save_update_offset(path, update_id):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump({"last_update_id": update_id}, f, ensure_ascii=True, indent=2)
        os.replace(tmp_path, path)
        return True
    except Exception as e:
        print(f"Failed to save update offset: {e}")
        return False


def _extract_requested_types(text):
    if not text:
        return []
    lower = text.lower()
    if "all" in lower:
        return list(AVAILABLE_TYPES)
    return [t for t in AVAILABLE_TYPES if t in lower]


def _build_sections(data_types):
    sections = {}

    if "domestic" in data_types:
        try:
            buy_trend, data = fetch_domestic_gold_prices()
            if data:
                sections["domestic"] = format_domestic_data(data, buy_trend)
            else:
                print(buy_trend)
        except Exception as e:
            print(f"Domestic fetch failed: {e}")

    if "international" in data_types:
        try:
            current_price_in_usd, change, current_price_in_vnd, exchange_rate_to_vnd = (
                fetch_international_gold_prices()
            )
            if change:
                sections["international"] = format_international_data(
                    current_price_in_usd, change, current_price_in_vnd, exchange_rate_to_vnd
                )
            else:
                print(current_price_in_usd)
        except Exception as e:
            print(f"International fetch failed: {e}")

    if "btmc" in data_types:
        try:
            data, status, err = fetch_btmc_gold_prices()
            if not err:
                sections["btmc"] = format_btmc_data(data, status)
            else:
                print(err)
        except Exception as e:
            print(f"BTMC fetch failed: {e}")

    return sections


def _compose_message(data_types, sections):
    now = datetime.now(timezone.utc) + timedelta(hours=7)
    current_time = now.strftime("%H:%M:%S")
    current_day = convert_day_to_vietnamese(now.strftime("%A"))
    current_date = now.strftime("%d/%m/%Y")

    header = [
        f"types: {', '.join(AVAILABLE_TYPES)}",
        f"requested: {', '.join(data_types)}",
        "\n"
    ]
    body = "\n\n".join([sections[t] for t in data_types if t in sections])
    message_body = "\n".join(header) + body
    return "```" + f"{current_time}\n" + f"{current_day} {current_date}\n" + message_body + "```"


def _handle_updates():
    state_path = _updates_state_path()
    last_update_id = _load_update_offset(state_path)
    offset = last_update_id + 1 if last_update_id is not None else None

    updates = get_updates(offset=offset, timeout=0)
    if not updates:
        print("No updates.")
        return

    max_update_id = last_update_id or 0
    for update in updates:
        update_id = update.get("update_id")
        if isinstance(update_id, int) and update_id > max_update_id:
            max_update_id = update_id

        message = (
            update.get("message")
            or update.get("channel_post")
            or update.get("edited_message")
        )
        if not message:
            continue

        text = message.get("text") or message.get("caption") or ""
        requested = _extract_requested_types(text)
        if not requested:
            continue

        chat_id = message.get("chat", {}).get("id")
        if chat_id is None:
            continue

        sections = _build_sections(requested)
        if not sections:
            continue

        payload = _compose_message(requested, sections)
        send_to_telegram(payload, chat_id=chat_id)

    if max_update_id and max_update_id != last_update_id:
        _save_update_offset(state_path, max_update_id)


def main(data_types):
    print("Starting gold price bot...")

    sections = _build_sections(data_types)
    if not sections:
        print("No data fetched successfully.")
        print("Gold price bot finished.")
        return

    message = _compose_message(data_types, sections)
    try:
        send_to_telegram(message)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

    print("Gold price bot finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gold Price Bot")
    parser.add_argument(
        "--type",
        nargs="+",
        choices=["domestic", "international", "btmc", "all"],
        default=["all"],
        help="Type(s) of gold data to fetch (default: all)",
    )
    parser.add_argument(
        "--check-updates",
        action="store_true",
        help="Check Telegram updates and reply based on requested types",
    )

    args = parser.parse_args()

    if args.check_updates:
        _handle_updates()
    else:
        if "all" in args.type:
            types = list(AVAILABLE_TYPES)
        else:
            types = args.type

        main(types)
