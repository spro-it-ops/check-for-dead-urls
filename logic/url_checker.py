import requests
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

class UrlChecker:
    """Performs HTTP checks on URLs."""
    @staticmethod
    def check_urls(urls_to_check, start_index, report_manager, num_workers=5):
        results = []
        print("Checking all page URLs...")

        def check_single(args):
            i, (url, sitemap_path) = args
            try:
                resp = requests.get(url, allow_redirects=True, timeout=10)
                status_code = resp.status_code
                logging.debug(f"Checked {url}: {status_code} (path: {' -> '.join(sitemap_path)})")
            except Exception as e:
                status_code = 0
                logging.debug(f"Error checking {url}: {e} (path: {' -> '.join(sitemap_path)})")
            return (i, url, status_code, sitemap_path)

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(check_single, (i, pair)): i for i, pair in enumerate(urls_to_check)}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Checking URLs"):
                i, url, status_code, sitemap_path = future.result()
                report_manager.append_check_result(start_index + i, url, status_code, sitemap_path)
                results.append((url, status_code, sitemap_path))

        return results