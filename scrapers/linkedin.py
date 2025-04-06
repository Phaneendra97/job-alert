from playwright.sync_api import sync_playwright
from utils import extract_company_from_url
import time

def fetch_linkedin_jobs(url: str, source: str):
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "application/json",
                "Origin": "https://www.linkedin.com",
                "Referer": url,
            }
        )

        page = context.new_page()
        print(f"🌐 Navigating to {source} job search page...")

        page.goto(url, timeout=60000)

        try:
            page.wait_for_selector("ul.jobs-search__results-list", timeout=15000)
        except Exception as e:
            print(f"⚠️ Job list container not found for {source}: {e}")
            browser.close()
            return []

        container_selector = "ul.jobs-search__results-list"
        previous_height = 0

        while True:
            page.evaluate(
                f'document.querySelector("{container_selector}").scrollTo(0, document.querySelector("{container_selector}").scrollHeight)'
            )
            time.sleep(2)

            current_height = page.evaluate(
                f'document.querySelector("{container_selector}").scrollHeight'
            )

            if current_height == previous_height:
                break
            previous_height = current_height

        print("✅ Finished scrolling.")

        job_cards = page.query_selector_all("ul.jobs-search__results-list li")
        if not job_cards:
            print(f"ℹ️ No job cards found for {source}.")
            browser.close()
            return []

        for card in job_cards:
            title_el = card.query_selector("h3.base-search-card__title")
            company_el = card.query_selector("h4.base-search-card__subtitle a")
            location_el = card.query_selector(".job-search-card__location")
            date_el = card.query_selector(".job-search-card__listdate--new")
            job_url = card.query_selector("a.base-card__full-link")

            dice_link = card.query_selector('a.hidden-nested-link')
            if dice_link and dice_link.inner_text().strip() == "Jobs via Dice":
                continue

            if not (title_el and company_el and location_el and job_url):
                continue

            base_card = card.query_selector("div.base-search-card")
            job_id_attr = base_card.get_attribute("data-entity-urn") if base_card else None
            if not job_id_attr:
                continue

            job_id = job_id_attr.split(":")[-1]
            jobs.append({
                "id": job_id,
                "title": title_el.inner_text().strip(),
                "company": source,
                "location": location_el.inner_text().strip(),
                "posted_date": date_el.inner_text().strip() if date_el else "Unknown",
                "url": job_url.get_attribute("href").strip(),
                "source": source
            })

        browser.close()

    print(f"✅ {source} scraper fetched {len(jobs)} jobs.")
    return jobs
