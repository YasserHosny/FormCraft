from datetime import datetime, time, timedelta
from uuid import UUID

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


class ReportSchedulerService:
    """Manages recurring report schedules using APScheduler."""

    def __init__(self, scheduler: AsyncIOScheduler | None = None):
        self.scheduler = scheduler or AsyncIOScheduler()
        self._jobs = {}

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self, wait=True):
        self.scheduler.shutdown(wait=wait)

    def compute_next_run(
        self,
        frequency: str,
        schedule_time: time,
        day_of_week: int | None,
        day_of_month: int | None,
        from_dt: datetime | None = None,
    ) -> datetime:
        """Compute the next run datetime for a schedule."""
        base = from_dt or datetime.utcnow()
        if frequency == "daily":
            candidate = base.replace(hour=schedule_time.hour, minute=schedule_time.minute, second=0, microsecond=0)
            if candidate <= base:
                candidate += timedelta(days=1)
            return candidate
        elif frequency == "weekly":
            # day_of_week: 0=Monday, 6=Sunday
            days_ahead = (day_of_week - base.weekday()) % 7
            candidate = base.replace(hour=schedule_time.hour, minute=schedule_time.minute, second=0, microsecond=0)
            candidate += timedelta(days=days_ahead)
            if candidate <= base:
                candidate += timedelta(weeks=1)
            return candidate
        elif frequency == "monthly":
            candidate = base.replace(
                day=min(day_of_month, 28),
                hour=schedule_time.hour,
                minute=schedule_time.minute,
                second=0,
                microsecond=0,
            )
            if candidate <= base:
                if candidate.month == 12:
                    candidate = candidate.replace(year=candidate.year + 1, month=1)
                else:
                    candidate = candidate.replace(month=candidate.month + 1)
            return candidate
        else:
            raise ValueError(f"Unknown frequency: {frequency}")

    def add_schedule(
        self,
        schedule_id: UUID,
        frequency: str,
        schedule_time: time,
        day_of_week: int | None,
        day_of_month: int | None,
        job_func,
        *args,
        **kwargs,
    ):
        """Add a recurring job to the scheduler."""
        if frequency == "daily":
            trigger = CronTrigger(
                hour=schedule_time.hour,
                minute=schedule_time.minute,
            )
        elif frequency == "weekly":
            trigger = CronTrigger(
                day_of_week=day_of_week,
                hour=schedule_time.hour,
                minute=schedule_time.minute,
            )
        elif frequency == "monthly":
            trigger = CronTrigger(
                day=min(day_of_month, 28),
                hour=schedule_time.hour,
                minute=schedule_time.minute,
            )
        else:
            raise ValueError(f"Unknown frequency: {frequency}")

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
        """Remove a recurring job from the scheduler."""
        sid = str(schedule_id)
        try:
            self.scheduler.remove_job(sid)
        except Exception:
            pass
        self._jobs.pop(sid, None)

    def pause_schedule(self, schedule_id: UUID):
        """Pause a recurring job."""
        sid = str(schedule_id)
        try:
            self.scheduler.pause_job(sid)
        except Exception:
            pass

    def resume_schedule(self, schedule_id: UUID):
        """Resume a paused recurring job."""
        sid = str(schedule_id)
        try:
            self.scheduler.resume_job(sid)
        except Exception:
            pass
