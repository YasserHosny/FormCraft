from datetime import datetime
from uuid import uuid4

from app.services.batch_schedule_service import BatchScheduleService


class TestBatchScheduleService:
    def test_compute_next_run_daily(self):
        svc = BatchScheduleService()
        next_run = svc.compute_next_run("0 9 * * *", from_dt=datetime(2026, 5, 26, 8, 0, 0))
        assert next_run.hour == 9
        assert next_run.minute == 0

    def test_add_and_remove_schedule(self):
        svc = BatchScheduleService()
        schedule_id = uuid4()

        def dummy_job():
            pass

        job = svc.add_schedule(schedule_id, "0 9 * * *", dummy_job)
        assert job is not None
        svc.remove_schedule(schedule_id)
        assert str(schedule_id) not in svc._jobs
