import asyncio
import logging
from celery import shared_task
from app.core.database import async_session_factory
from app.services.ai.tasks import ai_task_service

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.ai_celery_tasks.generate_long_script_task")
def generate_long_script_task(user_id: str, topic: str, duration: str = "10 minute"):
    """Background Celery task for generating comprehensive long-form video scripts."""
    async def _run():
        async with async_session_factory() as db:
            result = await ai_task_service.generate_script(
                db=db, user_id=user_id, topic=topic, script_format=duration
            )
            logger.info(f"Long script task completed for user {user_id}")
            return result

    return asyncio.run(_run())


@shared_task(name="app.tasks.ai_celery_tasks.batch_seo_audit_task")
def batch_seo_audit_task(user_id: str, video_list: list):
    """Background Celery task for batch auditing multiple video titles and SEO metadata."""
    async def _run():
        async with async_session_factory() as db:
            audit_results = []
            for video in video_list:
                res = await ai_task_service.analyze_seo(
                    db=db,
                    user_id=user_id,
                    title=video.get("title", ""),
                    description=video.get("description", ""),
                    tags=video.get("tags", "")
                )
                audit_results.append({"video_id": video.get("id"), "seo": res})
            return audit_results

    return asyncio.run(_run())
