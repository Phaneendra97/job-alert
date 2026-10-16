from urllib.parse import urlparse


def extract_company_from_url(job_url: str) -> str:
    domain = urlparse(job_url).netloc
    parts = domain.split(".")
    if len(parts) >= 2:
        return parts[-2].lower()  # e.g., servicenow from careers.servicenow.com
    return domain.lower()

# A job is kept only if its title contains at least one of these (case-insensitive)
TITLE_KEYWORDS = [
    "technical program manager",
    "technical project manager",
    "project manager",
    "program manager",
    "business analyst",
]


def matches_title_filter(job: dict) -> bool:
    title = (job.get("title") or "").lower()
    return any(keyword in title for keyword in TITLE_KEYWORDS)
