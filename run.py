import os
import argparse
from logic.app import SitemapCheckerApp

LIMIT_REQUESTS = 5000

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check URLs from sitemap")
    parser.add_argument("-r", "--resume", action="store_true", help="Resume from previous check")
    args = parser.parse_args()

    if os.path.exists("sitemap.txt"):
        with open("sitemap.txt", "r", encoding="utf-8") as f:
            line = f.readline().strip()
            if line:
                sitemap_url = line
            else:
                print("sitemap.txt is empty.")
                exit(1)
    else:
        print("sitemap.txt not found.")
        exit(1)

    app = SitemapCheckerApp(sitemap_url, resume=args.resume)
    app.run(limit_requests=LIMIT_REQUESTS if 'LIMIT_REQUESTS' in globals() else None)