import re
from playwright.sync_api import sync_playwright
from utils import extract_company_from_url

GOOGLE_URL = (
    "https://www.google.com/about/careers/applications/jobs/results"
    "?location=San%20Francisco%2C%20CA%2C%20USA"
    "&location=San%20Jose%2C%20CA%2C%20USA"
    "&location=Mountain%20View%2C%20CA%2C%20USA"
    "&location=Sunnyvale%2C%20CA%2C%20USA"
    "&q=%22Technical%20Program%20Manager%22"
    "&sort_by=date"
)

CARD_JS = """
cards => cards.map(card => {
    const link = card.querySelector('a[href*="jobs/results/"]');
    const title = card.querySelector('h3');
    const locs = Array.from(card.querySelectorAll('span.r0wTof')).map(e => e.textContent.trim());
    return {
        href: link ? link.href : null,
        title: title ? title.textContent.trim() : null,
        locations: locs
    };
})
"""

def fetch_jobs():
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 1024},
            locale="en-US",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("🌐 Navigating to Google job search...")
        page.goto(GOOGLE_URL, timeout=60000)

        try:
            page.wait_for_selector('li.lLd3Je a[href*="jobs/results/"]', timeout=20000)
        except Exception:
            print("❌ No Google job cards found")
            browser.close()
            return []

        cards = page.eval_on_selector_all("li.lLd3Je", CARD_JS)
        browser.close()

    for card in cards:
        href = card.get("href")
        if not href:
            continue

        # Drop the search query string so we store the canonical job link,
        # e.g. .../jobs/results/<id>-<slug>
        job_url = href.split("?")[0]
        match = re.search(r"/jobs/results/(\d+)", job_url)
        if not match:
            continue

        # The card repeats its location spans (and includes empty ones); dedupe in order
        locations = list(dict.fromkeys(l.lstrip("; ") for l in card.get("locations", []) if l.lstrip("; ")))

        jobs.append({
            "id": match.group(1),
            "title": card.get("title"),
            "location": "; ".join(locations),
            "url": job_url,
            "company": extract_company_from_url(job_url),
            "source": "google_site"
        })

    print(f"✅ Google scraper fetched {len(jobs)} jobs.")
    return jobs
