# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
scheduler.start()

def add_job(job_func, trigger, run_date=None, args=None):
    logger.info(f"Scheduling job {job_func.__name__} with trigger {trigger} at {run_date}")
    scheduler.add_job(job_func, trigger, run_date=run_date, args=args)
