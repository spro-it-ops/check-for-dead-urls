import requests
import xml.etree.ElementTree as ET
import logging

class SitemapCrawler:
    """Recursively crawls sitemaps."""
    def __init__(self):
        self.visited_sitemaps = set()
        self.inaccessible_sitemaps = []
        self.all_page_urls = []
        self.sitemap_levels = {}

    def fetch_all(self, start_url):
        print("Recursively fetching all page URLs from all sitemaps...")
        self._collect_recursive(start_url, level=0)

        logging.info(f"Total sitemaps collected: {len(self.sitemap_levels)}")
        logging.info(f"Total page URLs extracted: {len(self.all_page_urls)}")

        return self.all_page_urls, self.inaccessible_sitemaps, self.sitemap_levels

    def _collect_recursive(self, url, level):
        if url in self.visited_sitemaps:
            return

        self.visited_sitemaps.add(url)
        self.sitemap_levels[url] = level

        extracted_urls = self._fetch_and_parse(url)
        for child_url in extracted_urls:
            if "_sitemap" in child_url:
                self._collect_recursive(child_url, level + 1)
            else:
                self.all_page_urls.append(child_url)

    def _fetch_and_parse(self, url):
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            return [loc.text for loc in root.findall('.//ns:loc', ns)]
        except Exception as e:
            logging.error(f"Inaccessible sitemap: {url} ({e})")
            self.inaccessible_sitemaps.append(url)
            return []