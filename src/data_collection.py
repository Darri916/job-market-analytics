import os
import time
import csv
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

COUNTRIES = ["gb", "us", "au", "ca", "de", "fr", "nl", "sg", "nz", "at", "in"]

SEARCH_TERMS = [
    "data scientist",
    "data analyst",
    "machine learning engineer",
    "data engineer",
    "business intelligence analyst",
    "AI engineer",
    "MLOps engineer",
    "analytics engineer",
]
RESULTS_PER_PAGE = 50
MAX_PAGES = 20
BASE_URL = "https://api.adzuna.com/v1/api/jobs"

FIELDS = [
    "title", "company", "location", "country", "search_term",
    "salary_min", "salary_max", "description", "created", "redirect_url",
]

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "raw" / "jobs_raw.csv"
# OUTPUT_PATH = Path(__file__).parent.parent / "data" / "raw" / "jobs_india.csv"


def fetch_page(session: requests.Session, country: str, page: int, search_term: str) -> dict:
    url = f"{BASE_URL}/{country}/search/{page}"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": search_term,
        "content-type": "application/json",
    }
    response = session.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def extract_fields(job: dict, country: str, search_term: str) -> dict:
    return {
        "title": job.get("title", ""),
        "company": job.get("company", {}).get("display_name", ""),
        "location": job.get("location", {}).get("display_name", ""),
        "country": country.upper(),
        "search_term": search_term,
        "salary_min": job.get("salary_min", ""),
        "salary_max": job.get("salary_max", ""),
        "description": job.get("description", "").replace("\n", " ").strip(),
        "created": job.get("created", ""),
        "redirect_url": job.get("redirect_url", ""),
    }


def collect_jobs() -> list[dict]:
    all_jobs = []
    session = requests.Session()

    for search_term in SEARCH_TERMS:
        for country in COUNTRIES:
            print(f"[{search_term}] Collecting jobs for country: {country.upper()}")
            page = 1

            while page <= MAX_PAGES:
                try:
                    data = fetch_page(session, country, page, search_term)
                except requests.HTTPError as e:
                    print(f"  HTTP error on page {page}: {e}")
                    break
                except requests.RequestException as e:
                    print(f"  Request error on page {page}: {e}")
                    break

                jobs = data.get("results", [])
                if not jobs:
                    break

                for job in jobs:
                    all_jobs.append(extract_fields(job, country, search_term))

                total = data.get("count", 0)
                fetched = (page - 1) * RESULTS_PER_PAGE + len(jobs)
                print(f"  Page {page}: {len(jobs)} jobs (total fetched: {fetched} / {total})")

                if fetched >= total:
                    break

                page += 1
                time.sleep(0.5)

    return all_jobs


def save_to_csv(jobs: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(jobs)
    print(f"\nSaved {len(jobs)} jobs to {path}")


def main():
    if not APP_ID or not APP_KEY:
        raise EnvironmentError("ADZUNA_APP_ID and ADZUNA_APP_KEY must be set in .env")

    jobs = collect_jobs()
    save_to_csv(jobs, OUTPUT_PATH)


if __name__ == "__main__":
    main()
