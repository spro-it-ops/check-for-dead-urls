import os
import csv
import logging
from urllib.parse import unquote

class ReportManager:
    """Handles CSV reading/writing and directory management."""
    def __init__(self, config):
        self.config = config
        os.makedirs(self.config.reports_dir, exist_ok=True)

    def prepare_environment(self):
        """Clears previous data if not resuming."""
        if not self.config.resume:
            self._clear_directory(self.config.reports_dir)
            self._clear_directory(self.config.log_dir)

    def _clear_directory(self, directory):
        if os.path.exists(directory):
            print(f"Clearing directory: {directory}...")
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

    def load_checked_urls(self):
        """Loads state from the previous CSV report."""
        checked_urls = set()
        url_statuses = []

        if self.config.resume and os.path.exists(self.config.url_checks_csv):
            msg = f"Loading state from {self.config.url_checks_csv}..."
            print(msg)
            logging.info(msg)

            with open(self.config.url_checks_csv, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None) # Skip header
                count = 0
                for row in reader:
                    if len(row) >= 2:
                        url = unquote(row[1]).strip()
                        code = int(row[2])
                        checked_urls.add(url)
                        url_statuses.append((url, code))
                        count += 1

            msg = f"State loaded. {count} URLs already checked."
            print(f"{msg}\n")
            logging.info(msg)
        else:
            self._initialize_new_report()

        return checked_urls, url_statuses

    def _initialize_new_report(self):
        if self.config.resume:
            msg = f"Resume requested but {self.config.url_checks_csv} not found. Starting from scratch."
            print(msg)
            logging.info(msg)

        msg = "Initializing new URL check report..."
        print(msg)
        logging.info(msg)

        with open(self.config.url_checks_csv, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "url", "http_response_code"])

    def append_check_result(self, index, url, status_code):
        """Appends a single check result to the CSV file."""
        with open(self.config.url_checks_csv, "a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([index, url, status_code])

    def export_dead_sitemaps(self, inaccessible_sitemaps):
        with open(self.config.dead_sitemaps_csv, mode="w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "url", "http_response_code"])
            for idx, url in enumerate(inaccessible_sitemaps):
                writer.writerow([idx, url, 0])
        logging.info(f"Exported dead sitemaps to {self.config.dead_sitemaps_csv}")

    def export_sitemap_levels(self, sitemap_levels):
        with open(self.config.sitemap_levels_csv, mode="w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["sitemap_url", "tree_level"])
            for url, level in sitemap_levels.items():
                writer.writerow([url, level])
        logging.info(f"Exported sitemap levels to {self.config.sitemap_levels_csv}")