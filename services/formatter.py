import textwrap

def _split_price_and_change(value):
    v = (value or "").strip()
    if not v:
        return "", ""

    v = " ".join(v.split())

    if "▲" in v:
        price, rest = v.split("▲", 1)
        return price.strip(), ("▲" + rest.strip()).replace(" ", "")
    if "▼" in v:
        price, rest = v.split("▼", 1)
        return price.strip(), ("▼" + rest.strip()).replace(" ", "")

    parts = v.split(" ")
    if len(parts) >= 2 and parts[-1][:1] in ("+", "-"):
        return " ".join(parts[:-1]).strip(), parts[-1].strip()

    return v, ""


def format_domestic_data(data, buy_trend, col_widths=(10, 7, 7)):
    """Format danh sách dữ liệu giá vàng dưới dạng bảng (code block)."""
    print("Formatting data as code block...")

    type_width, buy_width, sell_width = col_widths
    line = f"+{'-' * (type_width + 2)}+{'-' * (buy_width + 2)}+{'-' * (sell_width + 2)}+"

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
        f"| {'Loại':<{type_width}} | {'Mua':<{buy_width}} | {'Bán':<{sell_width}} |",
        line,
    ]

    for row in data:
        gold_type = (row[0] if len(row) > 0 else "")
        buy_value = row[1] if len(row) > 1 else ""
        sell_value = row[2] if len(row) > 2 else ""

        gold_type = (gold_type or "").strip()
        buy_price, buy_change = _split_price_and_change(buy_value)
        sell_price, sell_change = _split_price_and_change(sell_value)

        buy_price = "LH" if buy_price.lower() == "liên hệ" else buy_price
        sell_price = "LH" if sell_price.lower() == "liên hệ" else sell_price

        buy_price = (buy_price or "")[:buy_width]
        sell_price = (sell_price or "")[:sell_width]
        buy_change = (buy_change or "")[:buy_width]
        sell_change = (sell_change or "")[:sell_width]

        wrapped_type = textwrap.wrap(gold_type, width=type_width) or [""]
        for i, type_line in enumerate(wrapped_type):
            buy_cell = buy_price if i == 0 else ""
            sell_cell = sell_price if i == 0 else ""
            table.append(f"| {type_line:<{type_width}} | {buy_cell:<{buy_width}} | {sell_cell:<{sell_width}} |")

        if buy_change or sell_change:
            table.append(f"| {'':<{type_width}} | {buy_change:<{buy_width}} | {sell_change:<{sell_width}} |")

        table.append(line)

    print("Data formatted successfully.")
    return "\n".join(table)

def format_international_data(current_price_in_usd, change, current_price_in_vnd, exchange_rate_to_vnd):
    def escape(text):
        special_chars = r'_*\[\]()~`>#+-=|{}.!'
        return ''.join(['\\' + c if c in special_chars else c for c in text])

    escaped_price = escape(current_price_in_usd)
    escaped_change = escape(change)

    if change.startswith('+'):
        emoji = "🟢"
    elif change.startswith('-'):
        emoji = "🔴"
    else:
        emoji = "⚪"

    message = (
            "Giá vàng quốc tế (USD): \n\n"
            f"{escaped_price} / 1 oz\n"
            f"{escaped_change} {emoji}"
    )

    exchange_message = (
            "\n\nQuy đổi:\n"
            f"1 USD = {exchange_rate_to_vnd} VND\n"
            f"{round(current_price_in_vnd, 0):,} / 1 lượng"
            ) if current_price_in_vnd is not None else ""

    return message + exchange_message

def format_btmc_data(data, status, col_widths=(12, 6, 6)):
    """
    Format danh sách dữ liệu giá vàng dưới dạng bảng (code block)
    """
    print("Formatting data as code block...")

    # Define column widths
    type_width, buy_width, sell_width = col_widths
    line = f"+{'-' * (type_width + 2)}+{'-' * (buy_width + 2)}+{'-' * (sell_width + 2)}+"

    emoji = ""
    if status == "increase":
        emoji = "🟢"
    elif status == "decrease":
        emoji = "🔴"
    elif status == "still":
        emoji = "⚪"

    # Header row
    table = [
        f"Giá vàng BTMC: {emoji}",
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
