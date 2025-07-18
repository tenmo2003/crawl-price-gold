import textwrap

def format_domestic_data(data, buy_trend):
    """
    Format danh sách dữ liệu giá vàng dưới dạng bảng (code block).
    """
    print("Formatting data as code block...")

    header = ["Loại", "Mua", "Bán"]
    line = "+------+--------------+--------------+"
    if buy_trend == 'increase':
        emoji = "🟢"
    elif buy_trend == 'decrease':
        emoji = "🔴"
    else:
        emoji = "⚪"

    table = [
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
    return "\n".join(table)

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
            "Giá vàng quốc tế (USD): \n\n"
            f"{escaped_price}\n"
            f"{escaped_change} {emoji}"
    )
    return message

def format_btmc_data(data, col_widths=(12, 6, 6)):
    """
    Format danh sách dữ liệu giá vàng dưới dạng bảng (code block)
    """
    print("Formatting data as code block...")

    # Define column widths
    type_width, buy_width, sell_width = col_widths
    line = f"+{'-' * (type_width + 2)}+{'-' * (buy_width + 2)}+{'-' * (sell_width + 2)}+"

    # Header row
    table = [
        "Giá vàng BTMC:",
        "",
        line,
        f"| {'Loại':<{type_width}} | {'Mua':<{buy_width}} | {'Bán':<{sell_width}} |",
        line,
    ]

    for row in data:
        gold_type = row[0]
        buy_price = row[1]
        sell_price = row[2]

        # Wrap the gold_type to the column width
        wrapped_type = textwrap.wrap(gold_type, width=type_width)
        lines = max(1, len(wrapped_type))

        for i in range(lines):
            type_line = wrapped_type[i] if i < len(wrapped_type) else ""
            buy_line = buy_price if i == 0 else ""
            sell_line = sell_price if i == 0 else ""
            buy_line = buy_line if buy_line.lower() != "liên hệ" else "LH"
            sell_line = sell_line if sell_line.lower() != "liên hệ" else "LH"
            table.append(
                f"| {type_line:<{type_width}} | {buy_line:<{buy_width}} | {sell_line:<{sell_width}} |"
            )
        table.append(line)

    print("Data formatted successfully.")
    return "\n".join(table)
