import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, Union
import time


class USDVNDConverter:
    def __init__(self, timeout: int = 10):
        """
        Initialize the converter

        Args:
            timeout (int): Request timeout in seconds (default: 10)
        """
        # Primary source: Vietcombank exchange-rate API (powers the public
        # Ty-gia page: https://www.vietcombank.com.vn/vi-VN/KHCN/Cong-cu-Tien-ich/Ty-gia)
        self.vietcombank_url = "https://www.vietcombank.com.vn/api/exchangerates?date=now"
        # Fallback source: investing.com (frequently 403s, kept as backup)
        self.url = "https://vn.investing.com/currencies/usd-vnd"
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self._cached_rate = None
        self._cache_timestamp = None
        self._cache_duration = 300  # Cache for 5 minutes
        self._last_source = None  # URL of the source that produced the current rate

    def _fetch_from_vietcombank(self) -> Optional[float]:
        """
        Fetch the USD/VND transfer rate from the Vietcombank exchange-rate API.

        Returns:
            float: USD transfer rate if successful, None otherwise
        """
        try:
            response = requests.get(
                self.vietcombank_url,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            payload = response.json()

            for entry in payload.get('Data', []):
                if entry.get('currencyCode') == 'USD':
                    # Use the transfer (chuyển khoản) rate as the reference rate
                    rate_str = str(entry.get('transfer', '')).replace(',', '')
                    rate = float(rate_str)
                    # Sanity check: USD/VND rate should be between 20,000 and 30,000
                    if 20000 <= rate <= 30000:
                        return rate
                    break
            return None
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching rate from Vietcombank: {e}")
            return None

    def _fetch_page_content(self) -> Optional[str]:
        """
        Fetch the HTML content from the investing.com page

        Returns:
            str: HTML content if successful, None otherwise
        """
        try:
            response = requests.get(
                self.url,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page content: {e}")
            return None

    def _extract_exchange_rate(self, html_content: str) -> Optional[float]:
        """
        Extract the USD/VND exchange rate from HTML content

        Args:
            html_content (str): HTML content to parse

        Returns:
            float: Exchange rate if found, None otherwise
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Common selectors where the rate might be displayed
            selectors = [
                'span[data-test="instrument-price-last"]',
                '.text-2xl',
                '[data-test="instrument-price-last"]',
                '.instrument-price_last__KQzyA',
                'span.text-2xl',
                '.pid-1175-last'
            ]

            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    rate_text = element.get_text().strip()
                    # Extract numeric value (handle comma separators)
                    rate_match = re.search(r'[\d,]+\.?\d*', rate_text)
                    if rate_match:
                        rate_str = rate_match.group().replace(',', '')
                        return float(rate_str)

            # Fallback: search for patterns in the entire HTML
            rate_patterns = [
                r'"last":(\d+\.?\d*)',
                r'"price":(\d+\.?\d*)',
                r'USD/VND[^\d]*(\d+\.?\d*)',
                r'(\d{5,}\.?\d*)'  # Look for 5+ digit numbers (typical VND rates)
            ]

            for pattern in rate_patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    try:
                        rate = float(match)
                        # Sanity check: USD/VND rate should be between 20,000 and 30,000
                        if 20000 <= rate <= 30000:
                            return rate
                    except ValueError:
                        continue

            return None

        except Exception as e:
            print(f"Error extracting exchange rate: {e}")
            return None

    def get_exchange_rate(self, use_cache: bool = True) -> Optional[float]:
        """
        Get the current USD to VND exchange rate

        Args:
            use_cache (bool): Whether to use cached rate if available

        Returns:
            float: Current exchange rate (1 USD = X VND), None if failed
        """
        # Check cache first
        if use_cache and self._is_cache_valid():
            return self._cached_rate

        # Primary strategy: Vietcombank API
        rate = self._fetch_from_vietcombank()
        if rate:
            self._update_cache(rate, self.vietcombank_url)
            return rate

        # Fallback strategy: investing.com scraping
        html_content = self._fetch_page_content()
        if html_content:
            rate = self._extract_exchange_rate(html_content)
            if rate:
                self._update_cache(rate, self.url)
                return rate

        # Last resort: return cached rate if available
        if self._cached_rate:
            print("Using cached rate due to fetch failure from all sources")
            return self._cached_rate

        return None

    def _update_cache(self, rate: float, source: str) -> None:
        """Store the freshly fetched rate and remember its source."""
        self._cached_rate = rate
        self._cache_timestamp = time.time()
        self._last_source = source

    def _is_cache_valid(self) -> bool:
        """Check if cached rate is still valid"""
        if not self._cached_rate or not self._cache_timestamp:
            return False
        return time.time() - self._cache_timestamp < self._cache_duration

    def convert_usd_to_vnd(self, usd_amount: Union[int, float]) -> Optional[float]:
        """
        Convert USD amount to VND

        Args:
            usd_amount (Union[int, float]): Amount in USD to convert

        Returns:
            float: Amount in VND, None if conversion failed
        """
        if usd_amount < 0:
            raise ValueError("Amount cannot be negative")

        rate = self.get_exchange_rate()
        if rate is None:
            print("Failed to get exchange rate")
            return None

        return usd_amount * rate

    def convert_vnd_to_usd(self, vnd_amount: Union[int, float]) -> Optional[float]:
        """
        Convert VND amount to USD

        Args:
            vnd_amount (Union[int, float]): Amount in VND to convert

        Returns:
            float: Amount in USD, None if conversion failed
        """
        if vnd_amount < 0:
            raise ValueError("Amount cannot be negative")

        rate = self.get_exchange_rate()
        if rate is None:
            print("Failed to get exchange rate")
            return None

        return vnd_amount / rate

    def get_rate_info(self) -> dict:
        """
        Get detailed information about the current exchange rate

        Returns:
            dict: Dictionary containing rate info and metadata
        """
        rate = self.get_exchange_rate()
        cache_valid = self._is_cache_valid()

        return {
            'rate': rate,
            'timestamp': time.time(),
            'cached': cache_valid,
            'cache_age': time.time() - self._cache_timestamp if self._cache_timestamp else None,
            'source': self._last_source or self.vietcombank_url
        }


# Convenience functions for direct usage
def get_usd_vnd_rate() -> Optional[float]:
    """Get current USD to VND exchange rate"""
    converter = USDVNDConverter()
    return converter.get_exchange_rate()


def usd_to_vnd(amount: Union[int, float]) -> Optional[float]:
    """Convert USD to VND"""
    converter = USDVNDConverter()
    return converter.convert_usd_to_vnd(amount)


def vnd_to_usd(amount: Union[int, float]) -> Optional[float]:
    """Convert VND to USD"""
    converter = USDVNDConverter()
    return converter.convert_vnd_to_usd(amount)


# Example usage
if __name__ == "__main__":
    # Create converter instance
    converter = USDVNDConverter()

    print("USD/VND Currency Converter")
    print("=" * 30)

    # Get current rate
    rate = converter.get_exchange_rate()
    if rate:
        print(f"Current exchange rate: 1 USD = {rate:,.2f} VND")

        # Example conversions
        usd_amounts = [1, 10, 100, 500]
        print(f"\nUSD to VND conversions:")
        for usd in usd_amounts:
            vnd = converter.convert_usd_to_vnd(usd)
            if vnd:
                print(f"${usd:,} USD = {vnd:,.0f} VND")

        vnd_amounts = [25000, 250000, 2500000]
        print(f"\nVND to USD conversions:")
        for vnd in vnd_amounts:
            usd = converter.convert_vnd_to_usd(vnd)
            if usd:
                print(f"{vnd:,} VND = ${usd:.2f} USD")

        # Show rate info
        info = converter.get_rate_info()
        print(f"\nRate info: {info}")
    else:
        print("Failed to get exchange rate")
