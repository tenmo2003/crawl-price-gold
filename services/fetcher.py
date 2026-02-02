import re
import requests
from bs4 import BeautifulSoup
from config import BTMC_URL, DOMESTIC_URL, INTERNATIONAL_URL, TIMEOUT
from services.vnd_usd_converter import USDVNDConverter

def fetch_domestic_gold_prices():
    """
    Lấy dữ liệu giá vàng từ URL được cấu hình.
    Trả về bộ (buy_trend, data_list).
    - buy_trend: 'increase', 'decrease', hoặc None (nếu không xác định)
    - data_list: danh sách các row dữ liệu dạng [Loại, Mua, Bán]
    """
    print("Fetching domestic gold prices...")
    try:
        response = requests.get(DOMESTIC_URL, timeout=TIMEOUT)
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
                    if not buy_change:
                        buy_change = ""
                        buy_symbol = ""
                    elif 'colorGreen' in buy_change_span['class']:
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
                    if not sell_change:
                        sell_change = ""
                        sell_symbol = ""
                    elif 'colorGreen' in sell_change_span['class']:
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
                    if buy_symbol == "▲":
                        buy_trend = "increase"
                    elif buy_symbol == "▼":
                        buy_trend = "decrease"
                    else:
                        buy_trend = "still"

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

def fetch_international_gold_prices():
    """
    Lấy dữ liệu giá vàng quốc tế.

    Trả về bộ (current_price_in_usd_or_err, change, current_price_in_vnd, exchange_rate_to_vnd)
    - current_price_in_usd_or_err: giá hiện tại (USD) hoặc thông báo lỗi
    - change: thay đổi giá (string) hoặc None nếu không lấy được
    """
    print("Fetching international gold prices...")
    try:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(INTERNATIONAL_URL, timeout=TIMEOUT, headers=headers)
        response.raise_for_status()
        print("Successfully fetched data from website.")
        soup = BeautifulSoup(response.content, 'html.parser')

        current_price_panel = soup.find('div', class_='border-b border-ktc-borders')
        if not current_price_panel:
            print("No current price panel found.")
            return "Không tìm thấy bảng giá hiện tại.", None, None, None

        current_price_element = current_price_panel.find('h3')
        if current_price_element is None:
            print("No current price found.")
            return "Không tìm thấy giá hiện tại.", None, None, None

        current_price_in_usd = current_price_element.get_text()
        current_price_in_usd = current_price_in_usd.replace(",", "")

        converter = USDVNDConverter()

        current_price_in_vnd = converter.convert_usd_to_vnd(float(current_price_in_usd))
        if current_price_in_vnd is not None:
            current_price_in_vnd /= 0.829 # convert from ounce to Tael

        exchange_rate_to_vnd = converter.get_exchange_rate()

        change_element = current_price_element.find_next_sibling('div', class_=re.compile("CommodityPrice"))
        if change_element is None:
            print("No change element found.")
            return "Không tìm thấy thay đổi giá.", None, current_price_in_vnd, exchange_rate_to_vnd

        change = change_element.get_text()

        return current_price_in_usd, change, current_price_in_vnd, exchange_rate_to_vnd
    except requests.RequestException as e:
        print(f"Error connecting to the website: {e}")
        return f"Lỗi khi kết nối đến trang web: {e}", None, None, None
    except Exception as e:
        print(f"Error parsing international gold prices: {e}")
        return f"Lỗi khi lấy dữ liệu giá vàng quốc tế: {e}", None, None, None

def fetch_btmc_gold_prices():
    print("Fetching BTMC Gold Prices...")
    try:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(BTMC_URL, timeout=TIMEOUT, headers=headers)
        response.raise_for_status()
        print("Successfully fetched data from website.")
        soup = BeautifulSoup(response.content, 'html.parser')

        price_table = soup.find('table', class_='bd_price_home')
        if not price_table:
            print("No current price panel found.")
            return [], "", "Không tìm thấy bảng giá hiện tại"

        table_rows = price_table.find_all('tr')
        if len(table_rows) < 2:
            print("No rows found in the data table.")
            return [], "", "Không tìm thấy bảng giá hiện tại"

        data = []
        status = ""
        for row in table_rows[1:]:
            shift = 0
            cols = row.find_all('td')
            if cols[0].get_attribute_list('rowspan'):
                shift = 1
            gold_type = cols[0+shift].get_text().strip()
            buy_price = cols[2+shift].get_text().strip()
            sell_price = cols[3+shift].get_text().strip()
            if status == "":
                try:
                    status_img_src = cols[4+shift].find('img').get_attribute_list('src')[0]
                    if "right_arrow" in status_img_src:
                        status = "still"
                    elif "up_arrow" in status_img_src:
                        status = "increase"
                    elif "down_arrow" in status_img_src:
                        status = "decrease"
                except Exception as e:
                    # i dont need ya then
                    print(e)
                    pass

            data.append([gold_type, buy_price, sell_price])

        return data, status, ""
    except requests.RequestException as e:
        print(f"Error connecting to the website: {e}")
        return [], "", f"Lỗi khi kết nối đến trang web: {e}"
    except Exception as e:
        print(f"Error parsing BTMC gold prices: {e}")
        return [], "", f"Lỗi khi lấy dữ liệu BTMC: {e}"
