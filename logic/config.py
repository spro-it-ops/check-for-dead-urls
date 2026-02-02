import os

class Config:
    """Holds configuration paths and settings."""
    def __init__(self, sitemap_url, resume=False, num_workers=10):
        self.sitemap_url = sitemap_url
        self.resume = resume
        self.limit_requests = None
        self.num_workers = num_workers  # Add this line

        self.log_dir = "log"
        self.reports_dir = "reports"

        self.log_file = os.path.join(self.log_dir, "check_urls.log")
        self.url_checks_csv = os.path.join(self.reports_dir, "url_checks.csv")
        self.dead_sitemaps_csv = os.path.join(self.reports_dir, "dead_sitemaps.csv")
        self.sitemap_levels_csv = os.path.join(self.reports_dir, "sitemap_levels.csv")