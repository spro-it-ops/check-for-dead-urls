import logging
from collections import Counter
from logic.config import Config
from logic.logger_setup import LoggerSetup
from logic.report_manager import ReportManager
from logic.sitemap_crawler import SitemapCrawler
from logic.url_checker import UrlChecker

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

    def run(self, limit_requests=None):
        # 1. Crawl Sitemaps
        all_urls, dead_sitemaps, levels = self.crawler.fetch_all(self.config.sitemap_url)

        # 2. Load Previous State
        checked_urls_set, existing_statuses = self.report_manager.load_checked_urls()

        # 3. Calculate urls needed to check
        urls_to_check = [u for u in all_urls if u not in checked_urls_set]

        if limit_requests:
            urls_to_check = urls_to_check[:limit_requests]

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
        counts = Counter(status for _, status in statuses)
        print("\nSummary of HTTP status codes:")
        for status, count in sorted(counts.items()):
            print(f"Status {status}: {count} URLs")

        inaccessible = counts.get(0, 0)
        print(f"Number of inaccessible URLs: {inaccessible}")

        logging.info(f"Status counts: {counts}")
        logging.info(f"Number of inaccessible URLs: {inaccessible}")