import subprocess
import os

# 📦 Ensure Chromium is installed before scraping
def ensure_playwright_browser_installed():
    browser_path = os.path.expanduser("~/.cache/ms-playwright/chromium")
    if not os.path.exists(browser_path):
        print("📦 Installing Chromium (Playwright)...")
        subprocess.run(["playwright", "install", "chromium"], check=True)

# Your imports
from scrapers.servicenow import fetch_jobs as fetch_servicenow_jobs
from supabase_utils import fetch_existing_job_ids, insert_new_jobs, log_error
from email_utils import send_job_alert_email
from scrapers.adobe import fetch_jobs as fetch_adobe_jobs
from scrapers.apple import fetch_jobs as fetch_apple_jobs
from scrapers.nvidia import fetch_jobs as fetch_nvidia_jobs
from scrapers.paypal import fetch_jobs as fetch_paypal_jobs
from scrapers.uber import fetch_jobs as fetch_uber_jobs
from scrapers.linkedin import fetch_linkedin_jobs

SCRAPERS = [
    fetch_servicenow_jobs,
    fetch_adobe_jobs,
    fetch_apple_jobs,
    fetch_nvidia_jobs,
    fetch_paypal_jobs,
    # fetch_uber_jobs,
    lambda: fetch_linkedin_jobs(
        "https://www.linkedin.com/jobs/search/?currentJobId=4388296709&distance=50&f_E=1%2C2%2C3&f_TPR=r3600&geoId=106233382&keywords=project%20manager&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=R", 
        "linkedin_project_manager"
    ),
     lambda: fetch_linkedin_jobs(
        "https://www.linkedin.com/jobs/search/?currentJobId=4388586727&distance=50&f_E=1%2C2%2C3&f_TPR=r3600&geoId=106233382&keywords=product%20manager&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true&sortBy=R", 
        "linkedin_product_manager"
    ),
    lambda: fetch_linkedin_jobs(
        "https://www.linkedin.com/jobs/search/?currentJobId=4388586727&distance=50&f_E=1%2C2%2C3&f_TPR=r3600&geoId=106233382&keywords=program%20manager&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true&sortBy=R",
        "linkedin_program_manager"
    ),
    lambda: fetch_linkedin_jobs(
        "https://www.linkedin.com/jobs/search/?currentJobId=4388735820&distance=50&f_E=1%2C2%2C3&f_TPR=r3600&geoId=106233382&keywords=scrum%20master&origin=JOB_SEARCH_PAGE_KEYWORD_AUTOCOMPLETE&refresh=true&sortBy=R",
        "linkedin_scrum_master"
    ),
    lambda: fetch_linkedin_jobs(
        "https://www.linkedin.com/jobs/search/?currentJobId=4402768395&distance=50&f_E=1%2C2%2C3&f_TPR=r3600&geoId=106233382&keywords=project%20manager%20intern&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true&sortBy=R",
        "linkedin_project_manager_intern"
    ),
]

def main():
    ensure_playwright_browser_installed()
    for scraper in SCRAPERS:
        try:
            jobs = scraper()  # Run the scraper
            if not jobs:
                continue

            company = jobs[0]["company"]
            source = jobs[0]["source"]

            print(f"📡 [{source}] Found {len(jobs)} jobs from {company}")

            existing_ids = fetch_existing_job_ids(source, company)
            new_jobs = [job for job in jobs if job["id"] not in existing_ids]

            if new_jobs:
                print(f"🆕 {len(new_jobs)} new job(s) for {company}")
                insert_new_jobs(new_jobs, source, company)
                send_job_alert_email(new_jobs, company)
            else:
                print(f"✅ No new jobs for {company}")

        except Exception as e:
            # Log the error to the database
            print(f"❌ Error occurred: {str(e)}")
            log_error(str(e), scraper.__name__)  # Log error with scraper name

if __name__ == "__main__":
    main()
