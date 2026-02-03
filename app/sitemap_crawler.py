import requests
import xml.etree.ElementTree as ET
import logging
from urllib.parse import unquote

class SitemapCrawler:
    """Recursively crawls sitemaps."""
    def __init__(self):
        self.visited_sitemaps = set()
        self.inaccessible_sitemaps = []
        self.all_page_urls = []  # Now stores (url, sitemap_path) tuples
        self.sitemap_levels = {}
        self.max_depth = 0

    def fetch_all(self, start_url):
        print("Recursively fetching all page URLs from all sitemaps...")
        self._collect_recursive(start_url, level=0, path=[start_url])

        logging.info(f"Total sitemaps collected: {len(self.sitemap_levels)}")
        logging.info(f"Total page URLs extracted: {len(self.all_page_urls)}")
        logging.info(f"Maximum sitemap depth: {self.max_depth}")

        return self.all_page_urls, self.inaccessible_sitemaps, self.sitemap_levels, self.max_depth

    def _collect_recursive(self, url, level, path):
        if url in self.visited_sitemaps:
            return

        self.visited_sitemaps.add(url)
        self.sitemap_levels[url] = level
        self.max_depth = max(self.max_depth, level + 1)

        extracted_urls = self._fetch_and_parse(url)
        for child_url in extracted_urls:
            if "_sitemap" in child_url:
                new_path = path + [child_url]
                self._collect_recursive(child_url, level + 1, new_path)
            else:
                # Store tuple with full sitemap path (excluding the page URL itself)
                self.all_page_urls.append((child_url, list(path)))

    def _fetch_and_parse(self, url):
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            return [unquote(loc.text).strip() for loc in root.findall('.//ns:loc', ns) if loc.text]
        except Exception as e:
            logging.error(f"Inaccessible sitemap: {url} ({e})")
            self.inaccessible_sitemaps.append(url)
            return []