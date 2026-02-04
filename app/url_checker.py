import requests
import logging
import time
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

            def attempt_request(timeout):
                try:
                    resp = requests.get(url, allow_redirects=True, timeout=timeout)
                    status_code = resp.status_code
                    logging.debug(f"Checked {url}: {status_code} (path: {' -> '.join(sitemap_path)})")
                    return status_code, None
                except Exception as e:
                    # Capture the reason
                    logging.debug(f"Error checking {url}: {e} (path: {' -> '.join(sitemap_path)})")
                    return 0, str(e)

            # Try 1: Initial attempt (10s timeout)
            timeout = 10
            status_code, reason = attempt_request(timeout)

            if status_code == 0:
                # Try 2: Wait 5s, increase timeout by 5s (15s)
                time.sleep(5)
                timeout += 5
                status_code, reason = attempt_request(timeout)

                if status_code == 0:
                    # Try 3: Wait 10s, increase timeout by 10s (25s)
                    time.sleep(10)
                    timeout += 10
                    status_code, reason = attempt_request(timeout)

                    if status_code == 0:
                        # Try 4: Wait 15s, increase timeout by 15s (40s)
                        time.sleep(15)
                        timeout += 15
                        status_code, reason = attempt_request(timeout)

            return (i, url, status_code, sitemap_path, reason)

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(check_single, (i, pair)): i for i, pair in enumerate(urls_to_check)}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Checking URLs"):
                i, url, status_code, sitemap_path, reason = future.result()

                # Standard report (no reason column)
                report_manager.append_check_result(start_index + i, url, status_code, sitemap_path)

                # Failure report (only for code 0)
                if status_code == 0:
                    report_manager.append_failure_result(start_index + i, url, status_code, sitemap_path, reason)

                results.append((url, status_code, sitemap_path))

        return results