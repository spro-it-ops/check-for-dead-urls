import logging
from collections import Counter
from app.config import Config
from app.logger_setup import LoggerSetup
from app.report_manager import ReportManager
from app.sitemap_crawler import SitemapCrawler
from app.url_checker import UrlChecker

class SitemapCheckerApp:
    """Main application controller."""
    def __init__(self, sitemap_url, resume=False):
        self.config = Config(sitemap_url, resume)
        self.report_manager = ReportManager(self.config)
        self.crawler = SitemapCrawler()

        # 1. Clean up if needed
        self.report_manager.prepare_environment()

        # 2. Setup logging
        LoggerSetup.setup(self.config)

        self._announce_mode()

    def _announce_mode(self):
        if self.config.resume:
            msg = "RESUME RUN DETECTED. Continuing from previous state."
        else:
            msg = "NEW RUN STARTED. Previous reports and logs cleared."
        print(f"\n{msg}\n")
        logging.info(msg)

    def run(self):
        # 1. Crawl Sitemaps
        all_urls_with_path, dead_sitemaps, levels, max_depth = self.crawler.fetch_all(self.config.sitemap_url)

        # Set max_depth in report_manager for proper column generation
        self.report_manager.set_max_depth(max_depth)

        if self.config.limit_requests:
            all_urls_with_path = all_urls_with_path[:self.config.limit_requests]
            logging.info('Requests capped at: %d', len(all_urls_with_path))

        # 2. Load Previous State
        checked_urls_set, existing_statuses = self.report_manager.load_checked_urls()

        # 3. Calculate urls needed to check (filter by URL, keep path info)
        urls_to_check = [(url, path) for url, path in all_urls_with_path if url not in checked_urls_set]

        # 4. Check URLs
        if urls_to_check:
            new_results = UrlChecker.check_urls(
                urls_to_check,
                start_index=len(checked_urls_set),
                report_manager=self.report_manager
            )
            existing_statuses.extend(new_results)
        else:
            msg = "All URLs have already been checked."
            print(msg)
            logging.info(msg)

        # 5. Summarize and Final Export
        self._summarize(existing_statuses)
        self.report_manager.export_dead_sitemaps(dead_sitemaps)
        self.report_manager.export_sitemap_levels(levels)

    def _summarize(self, statuses):
        counts = Counter(status for _, status, *_ in statuses)
        print("\nSummary of HTTP status codes:")
        for status, count in sorted(counts.items()):
            print(f"Status {status}: {count} URLs")

        inaccessible = counts.get(0, 0)
        print(f"Number of inaccessible URLs: {inaccessible}")

        logging.info(f"Status counts: {counts}")
        logging.info(f"Number of inaccessible URLs: {inaccessible}")

    @staticmethod
    def can_resume():
        """Check if a resume is possible (previous report exists)."""
        import os
        return os.path.exists("reports/url_checks.csv")

    @staticmethod
    def get_resume_info():
        """Get information about the previous run for resume."""
        import os
        import csv

        csv_path = "reports/url_checks.csv"
        if not os.path.exists(csv_path):
            return None

        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                count = sum(1 for _ in reader)
            return count
        except Exception:
            return None