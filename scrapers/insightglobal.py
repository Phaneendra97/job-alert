import requests
from utils import extract_company_from_url

# JSON API behind https://careers.insightglobal.com/insightglobal-careers/jobs
# (San Jose, 50 mile radius, keyword "Manager")
API_URL = "https://careers.insightglobal.com/api/jobs"
JOB_URL = "https://careers.insightglobal.com/insightglobal-careers/jobs/{slug}?lang=en-us"

PARAMS = {
    "stretchUnit": "MILES",
    "stretch": 50,
    "location": "San Jose",
    "keywords": "Manager",
    "sortBy": "relevance",
    "internal": "false",
    "tags5": "Insight Global (External)",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

MAX_PAGES = 10


def fetch_jobs():
    jobs = []
    seen = set()

    print("🌐 Fetching Insight Global jobs...")
    for page in range(1, MAX_PAGES + 1):
        response = requests.get(API_URL, params={**PARAMS, "page": page}, headers=HEADERS, timeout=30)
        response.raise_for_status()
        payload = response.json()
        results = payload.get("jobs", [])
        if not results:
            break

        for item in results:
            job = item.get("data", {})
            job_id = job.get("req_id") or job.get("slug")
            if not job_id or job_id in seen:
                continue
            seen.add(job_id)

            job_url = JOB_URL.format(slug=job.get("slug") or job_id)
            location = job.get("full_location") or job.get("location_name") or job.get("city")

            jobs.append({
                "id": job_id,
                "title": job.get("title"),
                "location": location,
                "url": job_url,
                "company": extract_company_from_url(job_url),
                "source": "insightglobal_site"
            })

        if len(seen) >= payload.get("totalCount", 0):
            break

    print(f"✅ Insight Global scraper fetched {len(jobs)} jobs.")
    return jobs
