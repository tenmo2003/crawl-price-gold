from datetime import datetime, timedelta, timezone
import argparse

from services.fetcher import fetch_btmc_gold_prices, fetch_domestic_gold_prices, fetch_international_gold_prices
from services.formatter import format_btmc_data, format_domestic_data, format_international_data
from services.telegram_bot import send_to_telegram
from utils.day_converter import convert_day_to_vietnamese

def main(data_type):
    print("Starting gold price bot...")

    message = ""

    if data_type in ("domestic", "all"):
        buy_trend, data = fetch_domestic_gold_prices()
        if data:
            message += format_domestic_data(data, buy_trend)
        else:
            print(buy_trend)

    if data_type in ("international", "all"):
        current_price, change = fetch_international_gold_prices()
        if change:
            if message:
                message += "\n\n"
            message += format_international_data(current_price, change)
        else:
            print(current_price)

    if data_type in ("btmc", "all"):
        data, err = fetch_btmc_gold_prices()
        if not err:
            message += format_btmc_data(data)
        else:
            print(err)

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
        choices=["domestic", "international", "btmc", "all"],
        default="all",
        help="Type of gold data to fetch (default: all)",
    )

    args = parser.parse_args()
    main(args.type)
