import requests
from urllib.parse import urljoin
from utils import extract_company_from_url

PAYPAL_SEARCH_URL = "https://paypal.eightfold.ai/api/pcsx/search"
PAYPAL_SEARCH_PARAMS = {
    "domain": "paypal.com",
    "query": "",
    "location": "San Jose, CA, United States",
    "sort_by": "timestamp",
    "filter_distance": 80,
    "filter_include_remote": 1,
    "filter_include_relocation": 0,
    "filter_job_category": "Program Management",
}
PAGE_SIZE = 10

def fetch_jobs():
    jobs = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Referer": (
            "https://paypal.eightfold.ai/careers?location=San+Jose%2C+CA%2C+United+States"
            "&sort_by=timestamp&filter_distance=80&filter_include_remote=1"
            "&filter_include_relocation=0&filter_job_category=Program+Management"
        ),
    }

    positions = []
    start = 0
    try:
        while True:
            params = {**PAYPAL_SEARCH_PARAMS, "start": start}
            response = requests.get(PAYPAL_SEARCH_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()["data"]
            page_positions = data.get("positions", [])
            positions.extend(page_positions)

            start += PAGE_SIZE
            if start >= data.get("count", 0) or not page_positions:
                break
    except Exception as e:
        print(f"❌ PayPal scraper failed: {e}")
        return []

    for job in positions:
        job_id = job.get("atsJobId") or job.get("displayJobId") or job.get("id")
        title = job.get("name")
        location = ", ".join(job.get("locations", [])) or "Unknown"
        url = urljoin("https://paypal.eightfold.ai", job.get("positionUrl", ""))
        posted_ts = job.get("postedTs")

        jobs.append({
            "id": job_id,
            "title": title,
            "location": location,
            "url": url,
            "company": extract_company_from_url(url),
            "source": "paypal_site",
            "posted_date": str(posted_ts) if posted_ts else "unknown"
        })

    print(f"💸 PayPal scraper fetched {len(jobs)} jobs.")
    return jobs
