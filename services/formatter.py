from datetime import datetime, timedelta, timezone
from utils.day_converter import convert_day_to_vietnamese

def format_domestic_data_as_code_block(data, buy_trend):
    """
    Format danh sách dữ liệu giá vàng dưới dạng bảng (code block).
    """
    print("Formatting data as code block...")
    now = datetime.now(timezone.utc) + timedelta(hours=7)
    current_time = now.strftime("%H:%M:%S")
    current_day = convert_day_to_vietnamese(now.strftime("%A"))
    current_date = now.strftime("%d/%m/%Y")

    header = ["Loại", "Mua", "Bán"]
    line = "+------+--------------+--------------+"
    if buy_trend == 'increase':
        emoji = "🟢"
    elif buy_trend == 'decrease':
        emoji = "🔴"
    else:
        emoji = "⚪"

    table = [
        f"{current_time}",
        f"{current_day} {current_date}",
        f"Giá vàng trong nước: {emoji}",
        "",
        line,
        f"| {header[0]:<4} | {header[1]:<12} | {header[2]:<12} |",
        line,
    ]

    for row in data:
        # Cắt chuỗi cho an toàn nếu quá dài
        gold_type = row[0][:4]
        buy_price = row[1]
        sell_price = row[2]
        table.append(f"| {gold_type:<4} | {buy_price:<12} | {sell_price:<12} |")

    table.append(line)

    print("Data formatted successfully.")
    return "```" + "\n".join(table) + "\n```"

def format_international_data(current_price, change):
    def escape(text):
        special_chars = r'_*\[\]()~`>#+-=|{}.!'
        return ''.join(['\\' + c if c in special_chars else c for c in text])

    escaped_price = escape(current_price)
    escaped_change = escape(change)

    if change.startswith('+'):
        emoji = "🟢"
    elif change.startswith('-'):
        emoji = "🔴"
    else:
        emoji = "⚪"

    message = (
            "```\n"
            "Giá vàng quốc tế (USD): \n\n"
            f"{escaped_price}\n"
            f"{escaped_change} {emoji}"
            "```"
    )
    return message
