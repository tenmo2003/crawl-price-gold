import requests
from bs4 import BeautifulSoup
from config import URL, TIMEOUT

def fetch_gold_prices():
    """
    Lấy dữ liệu giá vàng từ URL được cấu hình.
    Trả về bộ (buy_trend, data_list).
    - buy_trend: 'increase', 'decrease', hoặc None (nếu không xác định)
    - data_list: danh sách các row dữ liệu dạng [Loại, Mua, Bán]
    """
    print("Fetching gold prices...")
    try:
        response = requests.get(URL, timeout=TIMEOUT)
        response.raise_for_status()
        print("Successfully fetched data from website.")
        soup = BeautifulSoup(response.content, 'html.parser')

        table = soup.find('div', {'class': 'cate-24h-gold-pri-table'})
        if not table:
            print("No data table found.")
            return "Không tìm thấy dữ liệu giá vàng.", []

        rows = table.find('table', {'class': 'gia-vang-search-data-table'})
        if not rows:
            print("No rows found in the data table.")
            return "Không tìm thấy bảng giá vàng.", []

        data = []
        buy_trend = None  # 'increase' hoặc 'decrease'

        for row in rows.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 3:
                # Lấy giá mua
                buy_price_span = cols[1].find('span', {'class': 'fixW'})
                if not buy_price_span:
                    continue
                buy_price = buy_price_span.text.strip()

                buy_change_span = cols[1].find('span', {'class': ['colorGreen', 'colorRed']})
                if buy_change_span:
                    buy_change = buy_change_span.text.strip()
                    if 'colorGreen' in buy_change_span['class']:
                        buy_symbol = "▲"
                    elif 'colorRed' in buy_change_span['class']:
                        buy_symbol = "▼"
                    else:
                        buy_symbol = ""
                else:
                    buy_change = ""
                    buy_symbol = ""

                # Lấy giá bán
                sell_price_span = cols[2].find('span', {'class': 'fixW'})
                if not sell_price_span:
                    continue
                sell_price = sell_price_span.text.strip()

                sell_change_span = cols[2].find('span', {'class': ['colorGreen', 'colorRed']})
                if sell_change_span:
                    sell_change = sell_change_span.text.strip()
                    if 'colorGreen' in sell_change_span['class']:
                        sell_symbol = "▲"
                    elif 'colorRed' in sell_change_span['class']:
                        sell_symbol = "▼"
                    else:
                        sell_symbol = ""
                else:
                    sell_change = ""
                    sell_symbol = ""

                # Xác định xu hướng mua (buy_trend) nếu chưa có
                if buy_trend is None and buy_symbol:
                    buy_trend = 'increase' if buy_symbol == "▲" else 'decrease'

                # Ghép giá và xu hướng
                buy_price_full = f"{buy_price} {buy_symbol}{buy_change}".strip()
                sell_price_full = f"{sell_price} {sell_symbol}{sell_change}".strip()

                # Lấy tên loại vàng
                gold_type = cols[0].text.strip()

                data.append([gold_type, buy_price_full, sell_price_full])

        print(f"Buy trend: {buy_trend}")
        print("Data fetched successfully.")
        return buy_trend, data

    except requests.RequestException as e:
        print(f"Error connecting to the website: {e}")
        return f"Lỗi khi kết nối đến trang web: {e}", []
