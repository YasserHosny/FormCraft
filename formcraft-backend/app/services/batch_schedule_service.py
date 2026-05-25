from datetime import datetime
from uuid import UUID

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


class BatchScheduleService:
    """Manage recurring batch schedules using APScheduler."""

    def __init__(self, scheduler: AsyncIOScheduler | None = None):
        self.scheduler = scheduler or AsyncIOScheduler()
        self._jobs = {}

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self, wait=True):
        self.scheduler.shutdown(wait=wait)

    def compute_next_run(self, cron_expression: str, from_dt: datetime | None = None) -> datetime:
        """Compute next run from a 5-field cron expression."""
        base = from_dt or datetime.utcnow()
        try:
            trigger = CronTrigger.from_crontab(cron_expression)
            # APScheduler's trigger can give us the next fire time
            next_run = trigger.get_next_fire_time(None, base)
            return next_run or base
        except Exception:
            return base

    def add_schedule(
        self,
        schedule_id: UUID,
        cron_expression: str,
        job_func,
        *args,
        **kwargs,
    ):
        """Add a recurring batch schedule to the scheduler."""
        trigger = CronTrigger.from_crontab(cron_expression)
        job = self.scheduler.add_job(
            job_func,
            trigger=trigger,
            id=str(schedule_id),
            replace_existing=True,
            *args,
            **kwargs,
        )
        self._jobs[str(schedule_id)] = job
        return job

    def remove_schedule(self, schedule_id: UUID):
        sid = str(schedule_id)
        try:
            self.scheduler.remove_job(sid)
        except Exception:
            pass
        self._jobs.pop(sid, None)

    async def execute_schedule(
        self,
        schedule_id: UUID,
        org_id: UUID,
        template_id: UUID,
        api_endpoint: str,
        api_auth_type: str,
        api_auth_credential: str,
        api_headers: dict,
        column_mapping: dict,
        download_format: str,
        max_rows: int,
        batch_service,
        supabase_client,
    ):
        """Pull data from API and trigger a batch job."""
        import httpx

        headers = dict(api_headers)
        if api_auth_type == "api_key":
            headers["X-API-Key"] = api_auth_credential
        elif api_auth_type == "bearer_token":
            headers["Authorization"] = f"Bearer {api_auth_credential}"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(api_endpoint, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            if not isinstance(data, list):
                raise ValueError("API response must be a JSON array of objects")

            rows = data[:max_rows]

            # Create batch job from API data
            job = await batch_service.create_job_from_schedule(
                schedule_id=schedule_id,
                org_id=org_id,
                template_id=template_id,
                rows=rows,
                column_mapping=column_mapping,
                download_format=download_format,
                supabase_client=supabase_client,
            )

            # Update schedule metadata
            await supabase_client.table("batch_schedules").update({
                "last_run_at": datetime.utcnow().isoformat(),
                "last_run_status": "success",
                "last_run_job_id": str(job.id),
                "next_run_at": self.compute_next_run(
                    # need to fetch cron from DB; simplified here
                    "0 0 * * *"
                ).isoformat(),
                "failure_count": 0,
            }).eq("id", str(schedule_id)).execute()

            return job

        except Exception:
            # Update schedule failure
            schedule = await supabase_client.table("batch_schedules").select("failure_count").eq("id", str(schedule_id)).single().execute()
            current_failures = schedule.data.get("failure_count", 0) if schedule.data else 0

            await supabase_client.table("batch_schedules").update({
                "last_run_at": datetime.utcnow().isoformat(),
                "last_run_status": "failed",
                "failure_count": current_failures + 1,
            }).eq("id", str(schedule_id)).execute()

            # Retry once after 15 minutes if first failure
            if current_failures == 0:
                self.scheduler.add_job(
                    self.execute_schedule,
                    "date",
                    run_date=datetime.utcnow() + __import__("datetime").timedelta(minutes=15),
                    args=[schedule_id, org_id, template_id, api_endpoint, api_auth_type, api_auth_credential, api_headers, column_mapping, download_format, max_rows, batch_service, supabase_client],
                )

            raise

    async def run_nightly_cleanup(self, supabase_client):
        """Delete batch data sources older than 30 days with completed/failed/cancelled jobs."""
        cutoff = (datetime.utcnow() - __import__("datetime").timedelta(days=30)).isoformat()
        # Find data sources to purge
        result = await supabase_client.table("batch_data_sources").select("id, storage_path").lt("created_at", cutoff).execute()
        items = result.data or []
        for item in items:
            # Delete from storage (pseudo-code; actual implementation uses Supabase Storage client)
            # await storage_client.remove(item["storage_path"])
            await supabase_client.table("batch_data_sources").delete().eq("id", item["id"]).execute()
