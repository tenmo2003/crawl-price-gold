from datetime import datetime, timedelta, timezone
from utils.day_converter import convert_day_to_vietnamese

def format_as_code_block(data, buy_trend):
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
    icon = "📈" if buy_trend == 'increase' else "📉"

    table = [
        f"{current_time} {current_day} {current_date}",
        f"Giá vàng trong nước: {icon}",
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
