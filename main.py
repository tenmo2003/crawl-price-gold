from services.fetcher import fetch_gold_prices
from services.formatter import format_as_code_block
from services.telegram_bot import send_to_telegram
from config import USER_TAG

if __name__ == "__main__":
    print("Starting gold price bot...")

    buy_trend, data = fetch_gold_prices()

    # Nếu lấy được data (danh sách có dữ liệu)
    if data:
        # Gửi bảng giá vàng
        message = format_as_code_block(data, buy_trend)
        send_to_telegram(message)

        # Gửi gợi ý mua/bán
        if buy_trend == 'increase':
            send_to_telegram(
                f"Có nên mua vàng không má {USER_TAG} 🤔🤔🤔",
                parse_mode=None
            )
        elif buy_trend == 'decrease':
            send_to_telegram(
                f"✅ Mua vàng đi má {USER_TAG} 🧀🧀🧀",
                parse_mode=None
            )
    else:
        # buy_trend lúc này là thông báo lỗi (string)
        print(buy_trend)

    print("Gold price bot finished.")
