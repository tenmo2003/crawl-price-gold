from datetime import datetime, timedelta, timezone
import argparse

from services.fetcher import fetch_domestic_gold_prices, fetch_international_gold_prices
from services.formatter import format_domestic_data_as_code_block, format_international_data
from services.telegram_bot import send_to_telegram
from utils.day_converter import convert_day_to_vietnamese

def main(data_type):
    print("Starting gold price bot...")

    message = ""

    if data_type in ("domestic", "both"):
        buy_trend, data = fetch_domestic_gold_prices()
        if data:
            message += format_domestic_data_as_code_block(data, buy_trend)
        else:
            print(buy_trend)

    if data_type in ("international", "both"):
        current_price, change = fetch_international_gold_prices()
        if message:
            message += "\n\n"
        if change:
            message += format_international_data(current_price, change)
        else:
            print(current_price)

    # TODO: Add Bảo tín minh châu table

    if message:
        now = datetime.now(timezone.utc) + timedelta(hours=7)
        current_time = now.strftime("%H:%M:%S")
        current_day = convert_day_to_vietnamese(now.strftime("%A"))
        current_date = now.strftime("%d/%m/%Y")
        message = "```" + f"{current_time}\n" + f"{current_day} {current_date}\n" + message + "```"
        send_to_telegram(message)

    print("Gold price bot finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gold Price Bot")
    parser.add_argument(
        "--type",
        choices=["domestic", "international", "both"],
        default="both",
        help="Type of gold data to fetch (default: both)",
    )

    args = parser.parse_args()
    main(args.type)
