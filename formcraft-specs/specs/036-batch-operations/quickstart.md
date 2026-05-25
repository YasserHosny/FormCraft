# Quickstart: Batch Operations & Print Queue

## Local Development Setup

No new infrastructure dependencies are required beyond the existing stack (Python 3.12, Node.js 20+, Supabase CLI). Ensure the backend virtual environment has `openpyxl` installed (already present for reports).

```bash
cd formcraft-backend
source .venv/bin/activate
pip install -r requirements.txt  # already includes openpyxl
```

## Database Setup

Apply the F036 migration to your local Supabase instance:

```bash
supabase migration up
# or directly
psql $DATABASE_URL -f formcraft-backend/migrations/036_batch_operations.sql
```

Verify tables:

```sql
\dt batch_jobs
\dt batch_data_sources
\dt batch_schedules
\dt batch_errors
```

## Running the Backend

Start the FastAPI server as usual:

```bash
uvicorn app.main:app --reload --port 8000
```

The batch job routes are auto-registered under `/api/batch-jobs/`.

## Running the Frontend

Start the Angular dev server:

```bash
cd formcraft-frontend
ng serve
```

Navigate to `http://localhost:4200/desk/queue` after logging in as an operator or admin.

## Creating a Test Batch Job (Manual QA)

1. **Prepare a CSV**:
   ```csv
   customer_name,account_number,amount
   Ahmed Ali,123456789,1500.00
   Sara Khan,987654321,2500.50
   ```

2. **Create a published template** with fields whose keys match the CSV headers (or manually map them).

3. **Open the Batch Queue** (`/desk/queue`), click "New Batch Job".

4. **Select the template**, upload the CSV, verify auto-mapping.

5. **Run validation** and confirm all rows are green.

6. **Click Generate** and watch the progress bar update.

7. **Download ZIP** once completed and verify two PDFs with correct pre-filled data.

## Scheduled Batch Quick Test

1. **Create a mock API** that returns JSON:
   ```json
   [{ "customer_name": "Test", "account_number": "111", "amount": "100" }]
   ```

2. **Create a Batch Schedule** in the admin panel, set cron to `*/5 * * * *`, point to the mock API.

3. **Wait 5 minutes** and verify a new `batch_jobs` row appears with `scheduled_job_id` populated.

## API Contract Quick Test

Import `contracts/openapi.yaml` into Postman or Insomnia. Test:

- `POST /api/batch-jobs` — create job
- `GET /api/batch-jobs/{id}` — poll status
- `POST /api/batch-jobs/{id}/cancel` — cancel running job
- `GET /api/batch-jobs/{id}/download?format=zip` — download results
- `GET /api/batch-jobs/{id}/errors` — download error CSV
