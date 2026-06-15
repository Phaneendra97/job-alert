# job-alert

## How to Use

### Contributing
- Fork the repository or create a new branch.
- Add more companies to the scraper if needed.
- Create a Pull Request (PR) to contribute your changes.

### Prerequisites
- A [Supabase](https://supabase.com) account to manage your database.
- A [Render.com](https://render.com) account to deploy the service.

### Setting Up Supabase
1. Sign up or log in to your [Supabase](https://supabase.com) account.
2. Create a new project and note down the `SUPABASE_URL` and `SUPABASE_KEY` from the project settings.
3. In the "Database" section, create the necessary tables and schemas for the project. You can execute the following SQL queries in the SQL editor of your [Supabase](https://supabase.com) project:

```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    title TEXT,
    location TEXT,
    url TEXT,
    added_at TIMESTAMP DEFAULT NOW(),
    company TEXT,
    source TEXT,
    posted_date TEXT
);

CREATE TABLE job_scraper_errors (
    id SERIAL PRIMARY KEY,  -- Automatically increments the error record ID
    scraper_name VARCHAR(255) NOT NULL,  -- Name of the scraper that failed
    error_message TEXT NOT NULL,  -- Error message or exception details
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Time when the error occurred
);
```

To run these queries:
1. Navigate to the "SQL" section in your Supabase dashboard.
2. Open the SQL editor and paste the above queries.
3. Click "Run" to execute the queries and create the tables.

### Running Locally
1. Create a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2. Create an `.env` file with the following key-value pairs:
    ```env
    SUPABASE_URL=urlfordb
    SUPABASE_KEY=keeyyy
    DB_PASSWORD=pass
    EMAIL_ADDRESS=sender-email@gmail.com
    EMAIL_PASSWORD=your_app_email_password  # Refer: https://support.google.com/mail/answer/185833?hl=en
    EMAIL_RECIPIENT=email@gmail.com,yashumohan02@gmail.com  # Defaults to sender
    ```

### Deploying on Render.com
1. Create an account on [Render.com](https://render.com) and link your GitHub repository.
2. Select the "Cron Job" service.
3. Configure the following settings:
    - **Build Command:** `./build.sh`
    - **Start Command:** `python3 main.py`
    - **Schedule:** `0 * * * *` (to send emails every hour)
4. Deploy the service.
