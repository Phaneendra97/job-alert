from playwright.sync_api import sync_playwright
from utils import extract_company_from_url

ADOBE_URL = "https://careers.adobe.com/us/en/search-results?ak=1iykjkdv3glys"

def fetch_jobs():
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 1024},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("🌐 Navigating to Adobe job search...")
        page.on("response", lambda response: None)  # dummy init

        job_response_json = {}

        # Listen for /widgets JSON POST
        def handle_response(response):
            nonlocal job_response_json
            if "/widgets" in response.url and response.request.method == "POST":
                try:
                    json_data = response.json()
                    # ✅ Look specifically for eagerLoadRefineSearch.jobs
                    if "eagerLoadRefineSearch" in json_data:
                        job_data = json_data["eagerLoadRefineSearch"]["data"]
                        if "jobs" in job_data:
                            print(f"✅ Found jobs in eagerLoadRefineSearch: {len(job_data['jobs'])} jobs")
                            job_response_json = job_data
                except Exception as e:
                    print(f"⚠️ Failed to parse JSON: {e}")

        page.on("response", handle_response)
        # Visit the Adobe job search page
        page.goto(ADOBE_URL, timeout=60000)

        # Wait for the dropdown to be visible
        page.wait_for_selector("select#sortselect", timeout=15000)

        # Change sort to "Most recent"
        print("🔀 Switching sort to 'Most recent'...")
        page.select_option("select#sortselect", label="Most recent")
        selected = page.eval_on_selector("select#sortselect", "el => el.value")
        print(f"🧪 Sort value selected: {selected}")
        # Give time for request + render
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(8000)
        browser.close()

    if not job_response_json:
        print("❌ No jobs captured from Adobe /widgets")
        return []

    for job in job_response_json.get("jobs", []):
        job_url = job.get("applyUrl")
        if not job_url:
            continue

        job_id = job.get("jobId") or job.get("reqId")
        title = job.get("title")
        location = job.get("location") or job.get("cityStateCountry")

        jobs.append({
            "id": job_id,
            "title": title,
            "location": location,
            "url": job_url,
            "company": extract_company_from_url(job_url),
            "source": "adobe_site"
        })

    print(f"✅ Adobe scraper fetched {len(jobs)} jobs.")
    return jobs
