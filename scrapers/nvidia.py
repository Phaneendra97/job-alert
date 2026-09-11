from playwright.sync_api import sync_playwright
from utils import extract_company_from_url

NVIDIA_URL = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?locations=91336993fab910af6d702fae0bb4c2e8&locations=91336993fab910af6d716528e9d4c406&timeType=5509c0b5959810ac0029943377d47364&workerSubType=0c40f6bd1d8f10adf6dae161b1844a15&workerSubType=ab40a98049581037a3ada55b087049b7&workerSubType=0c40f6bd1d8f10adf6dae2cd57444a16&jobFamilyGroup=0c40f6bd1d8f10ae43ffc668c6847e8c"

def fetch_jobs():
    jobs = []
    job_response_json = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("🌐 Navigating to NVIDIA job search...")

        # Intercept /jobs response
        def handle_response(response):
            nonlocal job_response_json
            if "/NVIDIAExternalCareerSite/jobs" in response.url and response.request.method == "POST":
                try:
                    json_data = response.json()
                    job_response_json = json_data
                    print(f"✅ Captured job response with {len(json_data.get('jobPostings', []))} jobs")
                except Exception as e:
                    print(f"⚠️ Failed to parse NVIDIA JSON: {e}")

        page.on("response", handle_response)
        page.goto(NVIDIA_URL, timeout=60000)

        # Let network settle and trigger filters
        page.wait_for_timeout(7000)
        browser.close()

    # Parse jobs
    for job in job_response_json.get("jobPostings", []):
        title = job.get("title")
        job_id = job.get("bulletFields", [None])[0]
        location = job.get("locationsText", "Unknown")
        posted_on = job.get("postedOn", "Unknown")
        path = job.get("externalPath", "")
        url = "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite" + path

        jobs.append({
            "id": job_id,
            "title": title,
            "location": location,
            "url": url,
            "company": extract_company_from_url(url),
            "source": "nvidia_site",
            "posted_date": posted_on
        })

    print(f"🟢 NVIDIA scraper fetched {len(jobs)} jobs.")
    return jobs
