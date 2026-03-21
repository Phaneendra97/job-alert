from scrapers.linkedin import fetch_linkedin_jobs
import time

def verify():
    print("--- Test 1: Testing with non-existent job keyword for NO jobs condition ---")
    no_jobs_url = "https://www.linkedin.com/jobs/search/?keywords=akjhsdkjahsdkjhaskjdh&location=San%20Jose"
    results_no = fetch_linkedin_jobs(no_jobs_url, "linkedin_no_jobs_test")
    print(f"Results for No Jobs: {results_no}")
    
    print("\n--- Test 2: Testing with common search for existing jobs ---")
    jobs_url = "https://www.linkedin.com/jobs/search/?keywords=Software%20Engineer&location=San%20Jose"
    results_yes = fetch_linkedin_jobs(jobs_url, "linkedin_yes_jobs_test")
    print(f"Results for Yes Jobs count: {len(results_yes)}")

if __name__ == "__main__":
    verify()
