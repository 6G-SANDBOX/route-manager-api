# app/core/scheduler.py
import logging
from typing import Callable, Optional, Any
from apscheduler.schedulers.background import BackgroundScheduler


logger = logging.getLogger(__name__)

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def add_job(
    job_func: Callable[..., Any], 
    trigger: str, 
    run_date: Optional[str] = None, 
    args: Optional[list[Any]] = None
) -> None:
    """
    Schedules a job to be executed by the background scheduler.

    Args:
        job_func (Callable[..., Any]): The function to be executed as a job.
        trigger (str): The type of trigger to use (e.g., "date", "interval", "cron").
        run_date (Optional[str]): The specific time and date to run the job (required for 'date' trigger).
        args (Optional[list[Any]]): A list of arguments to pass to the job function.

    Returns:
        None
    """
    scheduler.add_job(job_func, trigger, run_date=run_date, args=args)

# TODO: Delete that function, but add loop constantly validating DBRoutes