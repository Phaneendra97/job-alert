import html
import re
import requests
from utils import extract_company_from_url

BASE_URL = "https://www.intelliswift.com"
OPENINGS_URL = f"{BASE_URL}/careers/current-openings"
SEARCH_URL = f"{BASE_URL}/careers/search_opening"
# The search box takes one phrase at a time, so each term is a separate query
SEARCH_TERMS = ["Program Manager", "Project Manager"]

# The site sits behind Akamai, which blocks headless Chromium but serves
# normal requests that carry real Chrome browser headers.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/134.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Each job card: <h3>title</h3> ... <h4>location</h4> ... <a href="/current-opening/<slug>">
CARD_RE = re.compile(
    r'<div class="post-title"><h3>(.*?)</h3></div>.*?'
    r'<div class="post-loction"><h4>(.*?)</h4></div>.*?'
    r'<a href="(/current-opening/[^"]+)"',
    re.S,
)


def is_california(location: str) -> bool:
    # Locations look like "CA - San Jose", "Newark, CA" or "CA - Remote"
    tokens = re.split(r"[\s,\-/()]+", location.upper())
    return "CA" in tokens or "CALIFORNIA" in tokens


def search(session, token, term):
    # Same request the site's search bar makes (Rails remote form)
    print(f"🔍 Searching Intelliswift for '{term}'...")
    response = session.post(
        SEARCH_URL,
        data={"authenticity_token": token, "filter[search_field]": term},
        headers={
            "X-CSRF-Token": token,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "text/javascript, application/javascript, */*; q=0.01",
            "Referer": OPENINGS_URL,
            "Origin": BASE_URL,
        },
        timeout=30,
    )
    response.raise_for_status()

    # The response is JS that injects escaped HTML; unescape it before parsing
    body = response.text.replace('\\"', '"').replace("\\/", "/").replace("\\n", "\n")
    results = CARD_RE.findall(body)
    print(f"   {len(results)} result(s) for '{term}'")
    return results


def fetch_jobs():
    jobs = []
    session = requests.Session()
    session.headers.update(HEADERS)

    print("🌐 Fetching Intelliswift openings page...")
    page = session.get(OPENINGS_URL, headers={"Accept": "text/html"}, timeout=30)
    page.raise_for_status()

    token = re.search(r'name="csrf-token" content="([^"]+)"', page.text)
    if not token:
        print("❌ Intelliswift CSRF token not found (page may be blocked)")
        return []
    token = token.group(1)

    seen = set()
    for term in SEARCH_TERMS:
        for raw_title, raw_location, path in search(session, token, term):
            location = html.unescape(raw_location).strip()
            if not is_california(location):
                continue

            # A job can match more than one term; keep it once
            slug = path.rsplit("/", 1)[-1]
            if slug in seen:
                continue
            seen.add(slug)

            job_url = f"{BASE_URL}{path}"
            jobs.append({
                "id": slug,
                "title": html.unescape(raw_title).strip(),
                "location": location,
                "url": job_url,
                "company": extract_company_from_url(job_url),
                "source": "intelliswift_site"
            })

    print(f"✅ Intelliswift scraper fetched {len(jobs)} CA jobs.")
    return jobs
