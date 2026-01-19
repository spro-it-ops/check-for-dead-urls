# Usage Instructions

## 1. Clone the Repository

```sh
git clone <repo-url>
cd check-for-dead-urls
```

## 2. Python Setup

Create and activate a virtual environment:

```sh
python3 -m venv venv
source venv/bin/activate
```

Install requirements (if requirements.txt exists):

```sh
pip install -r requirements.txt
```

## 3. Configure the Sitemap URL

- Rename `sitemap.txt.example` to `sitemap.txt`:

  ```sh
  mv sitemap.txt.example sitemap.txt
  ```

- Edit `sitemap.txt` and put the main sitemap URL on the first line.

## 4. Run the Script

Run a fresh check (clears previous reports and logs):

```sh
python check_urls.py
```

**Resume a previous check:**

If the script was interrupted, you can resume from where it left off using the `-r` or `--resume` flag. This will load the already checked URLs from `reports/` and continue checking the remaining ones.

```sh
python run.py --resume
# OR
python run.py -r
```

## 5. Output

- Reports will be saved in the `reports/` directory.
- Logs will be saved in the `log/` directory.