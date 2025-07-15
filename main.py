from services.fetcher import fetch_domestic_gold_prices, fetch_international_gold_prices
from services.formatter import format_domestic_data_as_code_block, format_international_data
from services.telegram_bot import send_to_telegram

if __name__ == "__main__":
    print("Starting gold price bot...")

    buy_trend, data = fetch_domestic_gold_prices()
    message = ""

    if data:
        message += format_domestic_data_as_code_block(data, buy_trend)
    else:
        print(buy_trend)

    current_price, change = fetch_international_gold_prices()
    if change:
        message += format_international_data(current_price, change)
    else:
        print(current_price)

    if message:
        send_to_telegram(message)

    print("Gold price bot finished.")
