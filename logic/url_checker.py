import requests
import logging
from tqdm import tqdm

class UrlChecker:
    """Performs HTTP checks on URLs."""
    @staticmethod
    def check_urls(urls_to_check, start_index, report_manager):
        results = []
        print("Checking all page URLs...")

        for i, url in enumerate(tqdm(urls_to_check, desc="Checking URLs")):
            try:
                resp = requests.get(url, allow_redirects=True, timeout=10)
                status_code = resp.status_code
                logging.debug(f"Checked {url}: {status_code}")
            except Exception as e:
                status_code = 0
                logging.error(f"Error checking {url}: {e}")

            # Save immediately (incremental state)
            report_manager.append_check_result(start_index + i, url, status_code)
            results.append((url, status_code))

        return results