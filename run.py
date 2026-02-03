import os
import argparse
from app.app import SitemapCheckerApp


def print_usage_instructions():
    """Print usage instructions and resume status."""
    print("\n" + "=" * 60)
    print("  URL Checker - Sitemap Dead Link Scanner")
    print("=" * 60)

    print("\nUSAGE:")
    print("  python run.py --start          Start a new URL check (clears previous data)")
    print("  python run.py --start --resume Resume from a previous interrupted check")
    print("  python run.py -s               Short form of --start")
    print("  python run.py -s -r            Short form of --start --resume")

    print("\nOPTIONS:")
    print("  -s, --start   Required flag to begin the URL checking process")
    print("  -r, --resume  Continue from previous check instead of starting fresh")

    print("\nPREREQUISITES:")
    # Check sitemap.txt
    if os.path.exists("sitemap.txt"):
        with open("sitemap.txt", "r", encoding="utf-8") as f:
            line = f.readline().strip()
            if line:
                print(f"  ✓ sitemap.txt found with URL: {line}")
            else:
                print("  ✗ sitemap.txt exists but is empty - please add a sitemap URL")
    else:
        print("  ✗ sitemap.txt not found - please create it from sitemap.txt.example")

    # Check resume possibility
    print("\nRESUME STATUS:")
    if SitemapCheckerApp.can_resume():
        count = SitemapCheckerApp.get_resume_info()
        if count is not None:
            print(f"  ✓ Previous run found with {count} URLs already checked")
            print("    Use '--start --resume' or '-s -r' to continue from where you left off")
        else:
            print("  ✓ Previous run found - use '--start --resume' to continue")
    else:
        print("  ○ No previous run found - '--resume' flag will have no effect")

    print("\nEXAMPLES:")
    print("  python run.py --start              # Fresh start")
    print("  python run.py --start --resume     # Continue previous check")
    print("  python run.py -s -r                # Same as above (short form)")
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check URLs from sitemap for dead links",
        add_help=True
    )
    parser.add_argument(
        "-s", "--start",
        action="store_true",
        help="Start the URL checking process (required to run)"
    )
    parser.add_argument(
        "-r", "--resume",
        action="store_true",
        help="Resume from previous check instead of starting fresh"
    )
    args = parser.parse_args()

    # If --start flag is not provided, show usage instructions
    if not args.start:
        print_usage_instructions()
        exit(0)

    # Validate sitemap.txt
    if os.path.exists("sitemap.txt"):
        with open("sitemap.txt", "r", encoding="utf-8") as f:
            line = f.readline().strip()
            if line:
                sitemap_url = line
            else:
                print("Error: sitemap.txt is empty.")
                print("Please add your sitemap URL to sitemap.txt")
                exit(1)
    else:
        print("Error: sitemap.txt not found.")
        print("Please create sitemap.txt from sitemap.txt.example and add your sitemap URL")
        exit(1)

    app = SitemapCheckerApp(sitemap_url, resume=args.resume)
    app.run()