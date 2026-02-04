import os
import csv
import logging
from urllib.parse import unquote

class ReportManager:
    """Handles CSV reading/writing and directory management."""
    def __init__(self, config):
        self.config = config
        self.max_depth = 0
        os.makedirs(self.config.reports_dir, exist_ok=True)

    def set_max_depth(self, max_depth):
        """Sets the maximum sitemap depth for column generation."""
        self.max_depth = max_depth

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

    def _get_csv_header(self):
        """Generates CSV header with dynamic sitemap level columns."""
        header = ["id"]
        for i in range(1, self.max_depth + 1):
            header.append(f"sitemap_l{i}")
        header.extend(["url", "http_response_code"])
        return header

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
                header = next(reader, None)  # Read header to determine structure
                if header:
                    # Find the index of 'url' and 'http_response_code' columns
                    url_idx = header.index("url") if "url" in header else -1
                    code_idx = header.index("http_response_code") if "http_response_code" in header else -1

                    # Determine max_depth from header (count sitemap_l columns)
                    sitemap_cols = [col for col in header if col.startswith("sitemap_l")]
                    if sitemap_cols and self.max_depth == 0:
                        self.max_depth = len(sitemap_cols)

                    count = 0
                    for row in reader:
                        if len(row) > max(url_idx, code_idx) and url_idx >= 0 and code_idx >= 0:
                            url = unquote(row[url_idx]).strip()
                            code = int(row[code_idx])
                            # Extract sitemap path from row
                            sitemap_path = []
                            for i, col in enumerate(header):
                                if col.startswith("sitemap_l") and i < len(row):
                                    sitemap_path.append(row[i])
                            checked_urls.add(url)
                            url_statuses.append((url, code, sitemap_path))
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
            writer.writerow(self._get_csv_header())

        # Initialize failure report with reason column
        with open(self.config.failed_urls_csv, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            header = self._get_csv_header()
            header.append("failure_reason")
            writer.writerow(header)

    def append_check_result(self, index, url, status_code, sitemap_path):
        """Appends a single check result to the CSV file."""
        with open(self.config.url_checks_csv, "a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            row = [index]
            # Pad sitemap_path to max_depth
            padded_path = sitemap_path + [""] * (self.max_depth - len(sitemap_path))
            row.extend(padded_path)
            row.extend([url, status_code])
            writer.writerow(row)

    def append_failure_result(self, index, url, status_code, sitemap_path, reason):
        """Appends a failed check result with reason to the failure report."""
        # Check if file exists to handle resume cases where it might be missing
        file_exists = os.path.exists(self.config.failed_urls_csv)

        with open(self.config.failed_urls_csv, "a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                header = self._get_csv_header()
                header.append("failure_reason")
                writer.writerow(header)

            row = [index]
            # Pad sitemap_path to max_depth
            padded_path = sitemap_path + [""] * (self.max_depth - len(sitemap_path))
            row.extend(padded_path)
            row.extend([url, status_code, reason])
            writer.writerow(row)

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