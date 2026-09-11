from playwright.sync_api import sync_playwright
from utils import extract_company_from_url
from urllib.parse import urljoin

APPLE_URL = "https://jobs.apple.com/en-us/search?location=sunnyvale-SVL+cupertino-CUP+santa-clara-SNC+santa-clara-valley-cupertino-SCV+san-francisco-bay-area-SFMETRO&key=project%2520manager+program%2520manager"

def fetch_jobs():
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("🌐 Navigating to Apple job search...")
        page.goto(APPLE_URL, timeout=60000)
        page.wait_for_selector("#search-job-list li", timeout=15000)

        job_cards = page.query_selector_all("#search-job-list li")

        print(f"✅ Found {len(job_cards)} Apple job cards")

        for card in job_cards:
            link_el = card.query_selector("a.link-inline")
            location_el = card.query_selector("span#search-store-name-container-1")
            date_el = card.query_selector(".job-posted-date")

            if not link_el:
                continue

            title = link_el.inner_text().strip()
            href = link_el.get_attribute("href").strip()
            job_id = href.split("/")[3]  # e.g., /en-us/details/200596279/...
            location = location_el.inner_text().strip() if location_el else "Unknown"
            posted_date = date_el.inner_text().strip() if date_el else "Unknown"

            full_url = urljoin("https://jobs.apple.com", href)

            jobs.append({
                "id": job_id,
                "title": title,
                "location": location,
                "url": full_url,
                "company": extract_company_from_url(full_url),
                "source": "apple_site",
                "posted_date": posted_date
            })

        browser.close()

    print(f"🍎 Apple scraper fetched {len(jobs)} jobs.")
    return jobs
