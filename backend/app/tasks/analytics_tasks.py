import logging
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.refresh_channel_analytics")
def refresh_channel_analytics(channel_id: str):
    logger.info(f"Refreshing YouTube Data API analytics for channel: {channel_id}")
    return {"channel_id": channel_id, "status": "analytics_updated"}


@celery_app.task(name="tasks.generate_weekly_pdf_report")
def generate_weekly_pdf_report(user_id: str):
    logger.info(f"Generating weekly growth PDF report for user: {user_id}")
    return {"user_id": user_id, "status": "pdf_report_ready"}
