from datetime import datetime, timedelta, timezone
import argparse

from services.fetcher import fetch_btmc_gold_prices, fetch_domestic_gold_prices, fetch_international_gold_prices
from services.formatter import format_btmc_data, format_domestic_data, format_international_data
from services.telegram_bot import send_to_telegram
from utils.day_converter import convert_day_to_vietnamese

def main(data_types):
    print("Starting gold price bot...")

    message = ""

    if "international" in data_types:
        try:
            current_price_in_usd, change, current_price_in_vnd, exchange_rate_to_vnd = fetch_international_gold_prices()
            if change:
                if message:
                    message += "\n\n"
                message += format_international_data(current_price_in_usd, change, current_price_in_vnd, exchange_rate_to_vnd)
            else:
                print(current_price_in_usd)
        except Exception as e:
            print(f"International fetch failed: {e}")

    if "domestic" in data_types:
        try:
            buy_trend, data = fetch_domestic_gold_prices()
            if data:
                if message:
                    message += "\n\n"
                message += format_domestic_data(data, buy_trend)
            else:
                print(buy_trend)
        except Exception as e:
            print(f"Domestic fetch failed: {e}")

    if "btmc" in data_types:
        try:
            data, status, err = fetch_btmc_gold_prices()
            if not err:
                if message:
                    message += "\n\n"
                message += format_btmc_data(data, status)
            else:
                print(err)
        except Exception as e:
            print(f"BTMC fetch failed: {e}")

    if message:
        now = datetime.now(timezone.utc) + timedelta(hours=7)
        current_time = now.strftime("%H:%M:%S")
        current_day = convert_day_to_vietnamese(now.strftime("%A"))
        current_date = now.strftime("%d/%m/%Y")
        message = "```" + f"{current_time}\n" + f"{current_day} {current_date}\n" + message + "```"
        try:
            send_to_telegram(message)
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")

    print("Gold price bot finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gold Price Bot")
    parser.add_argument(
        "--type",
        nargs='+',
        choices=["domestic", "international", "btmc", "all"],
        default=["all"],
        help="Type(s) of gold data to fetch (default: all)",
    )

    args = parser.parse_args()

    # Handle special 'all' keyword
    if "all" in args.type:
        types = ["domestic", "international", "btmc"]
    else:
        types = args.type

    main(types)
