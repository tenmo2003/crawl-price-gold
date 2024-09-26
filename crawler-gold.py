import asyncio
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime

def capture_screenshot(url):
    # Setup the Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Set the window size to 1280x720
    driver.set_window_size(1280, 720)
    
    # Open the webpage
    driver.get(url)
    
    # Wait for the page to load completely
    driver.implicitly_wait(10)
    
    # Scroll to the desired section
    element = driver.find_element(By.XPATH, "//div[@id='gold-price']")
    driver.execute_script("arguments[0].scrollIntoView();", element)
    
    # Take screenshot
    png = driver.get_screenshot_as_png()
    
    # Close the driver
    driver.quit()
    
    return png

async def send_telegram_photo(token, chat_id, photo, caption=None):
    bot = Bot(token=token)
    with BytesIO(photo) as photo_file:
        photo_file.seek(0)
        await bot.send_photo(chat_id=chat_id, photo=photo_file, caption=caption, parse_mode=ParseMode.MARKDOWN)

if __name__ == "__main__":
    url = "https://dantri.com.vn/gia-vang.htm"
    
    # Capture screenshot
    screenshot = capture_screenshot(url)
    
    # Prepare the caption
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    caption = f"💰 *Giá vàng hôm nay*\n📅 *Cập nhật:* _{current_time}_\n[🔗 Detail](https://dantri.com.vn/gia-vang.htm)"
    
    # Send screenshot via Telegram
    token = '' #add token telegram bot
    chat_id = '' #add chat id telegram
    asyncio.run(send_telegram_photo(token, chat_id, screenshot, caption))
