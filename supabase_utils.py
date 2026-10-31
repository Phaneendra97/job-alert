from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_existing_job_ids(job_ids: list) -> set:
    """Return which of the given job IDs already exist in Supabase."""
    existing = set()
    chunk_size = 200  # keep the request URL a reasonable length
    for i in range(0, len(job_ids), chunk_size):
        chunk = job_ids[i:i + chunk_size]
        response = supabase.table("jobs").select("id").in_("id", chunk).execute()
        existing.update(item["id"] for item in response.data or [])
    return existing

def insert_new_jobs(jobs: list, source: str, company: str) -> list:
    """Insert jobs not already in Supabase and return the ones actually inserted."""
    existing_ids = fetch_existing_job_ids([job["id"] for job in jobs])

    new_jobs = []
    for job in jobs:
        if job["id"] in existing_ids:
            continue
        existing_ids.add(job["id"])  # also drops duplicates within this batch
        job["source"] = source
        job["company"] = company
        new_jobs.append(job)

    if new_jobs:
        supabase.table("jobs").insert(new_jobs).execute()
    return new_jobs

def log_error(error_message: str, scraper_name: str):
    """Log errors into the database."""
    try:
        supabase.table("job_scraper_errors").insert({
            "scraper_name": scraper_name,
            "error_message": error_message
        }).execute()
        print(f"🔴 Error logged for scraper: {scraper_name}")
    except Exception as e:
        print(f"❌ Failed to log error: {str(e)}")